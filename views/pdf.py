import copy
import json
import logging
import os
import shutil
import struct
import subprocess
import tempfile
from pathlib import Path
from typing import Any, ClassVar

import pdfkit
import pypandoc
from django.conf import settings
from django.contrib.staticfiles.finders import find as find_static_file
from django.http import FileResponse, HttpResponse
from django.template import Context, Template
from django.template.loader import get_template, select_template

from mighty.apps import MightyConfig
from mighty.views.crud import DetailView

logger = logging.getLogger(__name__)


class PDFView(DetailView):
    """View for generating PDF and Word documents from HTML templates."""

    cache_object = None
    tmp_files: ClassVar[list[str]] = []
    post_data: ClassVar[dict[str, Any]] = {}
    in_browser = False

    # Configurables
    pdf_name = 'file.pdf'
    options: ClassVar[dict[str, Any]] = MightyConfig.pdf_options.copy()
    header_tpl = MightyConfig.pdf_header
    footer_tpl = MightyConfig.pdf_footer
    content_html = MightyConfig.pdf_content
    config: ClassVar[dict[str, Any]] = {}

    @property
    def current_config(self) -> dict[str, Any]:
        """Get current configuration."""
        return self.config

    @property
    def filename(self) -> str:
        """Get PDF filename."""
        return self.pdf_name

    def post(self, request, *args, **kwargs):
        """Handle POST request by parsing JSON data."""
        self.post_data = json.loads(request.body.decode('utf-8'))
        return self.get(request, *args, **kwargs)

    def get_object(self):
        """Get the cached object or fetch it from parent class."""
        if not self.cache_object:
            self.cache_object = super().get_object()
        return self.cache_object

    def get_context_data(self, **kwargs):
        """Get context data for template rendering."""
        return Context({'obj': self.get_object()})

    def has_option(self, key: str) -> bool:
        """Check if an option is enabled in request or config."""
        config_value = self.current_config.get(key, False)
        return bool(self.request.GET.get(key, config_value))

    def _pdf_margin_side_from_config(self, side: str) -> str | None:
        """Read margin-top / margin_bottom (or hyphenated) from current_config."""
        cfg = self.current_config
        for key in (f'margin_{side}', f'margin-{side}'):
            val = cfg.get(key)
            if val not in (None, ''):
                return str(val)
        return None

    def render_section(self, template_str: str, context: Context) -> str:
        """Render a template section with given context."""
        return Template(template_str).render(context)

    def build_template_content(self, context: Context) -> str:
        """Build rendered template content."""
        # Check if there's a custom get_template method (like in ConvenePDFView)
        if hasattr(self, 'get_template') and callable(self.get_template):
            # Use the custom get_template method for backward compatibility
            return self.get_template(context)

        # Standard template resolution
        template_names = self.get_template_names()
        # Handle case where get_template_names() returns a list
        if isinstance(template_names, list):
            template = select_template(template_names)
        else:
            template = get_template(template_names)
        return self.content_html % template.render(context)

    def render_to_response(self, context, **response_kwargs):
        """Render the final response (PDF or Word document)."""
        self._prepare_pdf_options()
        self.html_content = self.build_template_content(context)

        # Handle Word export first
        if self.post_data.get('action') == 'word':
            return self._create_word_response(context)

        # Generate PDF, save if requested, otherwise create temporary
        pdf_path = (
            self._save_pdf()
            if self.request.GET.get('save')
            else self._generate_pdf_file(self.html_content)
        )

        # Handle browser or download response
        return (
            self._create_browser_response(pdf_path)
            if self.in_browser
            else self._create_download_response(pdf_path)
        )

    def _create_temp_html_file(self, html_content: str) -> str:
        """Create a temporary HTML file and return its path."""
        with tempfile.NamedTemporaryFile(
            suffix='.html', delete=False
        ) as temp_file:
            temp_file_path = temp_file.name

        with Path(temp_file_path).open('wb') as temp_file:
            temp_file.write(html_content.encode('utf-8'))
        self.tmp_files.append(temp_file_path)
        return temp_file_path

    def _build_header_html(self) -> str:
        """Build header HTML if enabled."""
        if self.has_option('header_enable'):
            html = self.render_section(
                self._get_header_template(), self.get_context_data()
            )
            html = self._inject_font_face_style(html)
            return self._create_temp_html_file(html)
        return ''

    def _build_footer_html(self) -> str:
        """Build footer HTML if enabled."""
        if self.has_option('footer_enable'):
            html = self.render_section(
                self._get_footer_template(), self.get_context_data()
            )
            html = self._inject_font_face_style(html)
            return self._create_temp_html_file(html)
        return ''

    def _get_header_template(self) -> str:
        """Get header template."""
        return ''

    def _get_footer_template(self) -> str:
        """Get footer template."""
        return ''

    @staticmethod
    def _wkhtmltoimage_bin() -> str | None:
        path = shutil.which('wkhtmltoimage')
        if path:
            return path
        wkpdf = shutil.which('wkhtmltopdf')
        if wkpdf:
            sibling = Path(wkpdf).with_name('wkhtmltoimage')
            if sibling.is_file():
                return str(sibling)
        return None

    def _pdf_screen_dpi(self) -> int:
        raw = self.options.get('dpi')
        if raw in (None, ''):
            return 96
        try:
            return int(raw)
        except (TypeError, ValueError):
            return 96

    @staticmethod
    def _a4_page_width_mm(orientation: str) -> float:
        if (orientation or 'Portrait').lower() == 'landscape':
            return 297.0
        return 210.0

    def _page_width_px_for_pdf(self, orientation: str) -> int:
        mm = self._a4_page_width_mm(orientation)
        dpi = self._pdf_screen_dpi()
        return max(1, int(round(mm / 25.4 * dpi)))

    @staticmethod
    def _read_png_pixel_height(png_path: Path) -> int:
        with png_path.open('rb') as f:
            if f.read(8) != b'\x89PNG\r\n\x1a\n':
                msg = 'not a PNG'
                raise ValueError(msg)
            while True:
                chunk_head = f.read(8)
                if len(chunk_head) < 8:
                    msg = 'truncated PNG'
                    raise ValueError(msg)
                chunk_len, chunk_type = struct.unpack('>I4s', chunk_head)
                chunk_data = f.read(chunk_len)
                f.read(4)
                if chunk_type == b'IHDR':
                    _, height = struct.unpack('>II', chunk_data[:8])
                    return height

    def _run_wkhtmltoimage(
        self,
        bin_path: str,
        source_html_path: Path,
        png_path: Path,
        width_px: int,
    ) -> bool:
        html_abs = str(source_html_path.resolve())
        png_abs = str(png_path.resolve())
        base = [
            bin_path,
            '--quiet',
            '--javascript-delay',
            '200',
            '--width',
            str(width_px),
            html_abs,
            png_abs,
        ]
        for with_local_access in (True, False):
            cmd = list(base)
            if with_local_access:
                cmd.insert(1, '--enable-local-file-access')
            try:
                subprocess.run(
                    cmd,
                    check=True,
                    capture_output=True,
                    timeout=45,
                    text=True,
                )
            except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
                logger.warning('wkhtmltoimage failed: %s', exc)
                return False
            except subprocess.CalledProcessError as exc:
                err = (exc.stderr or exc.stdout or '')[:800]
                logger.debug(
                    'wkhtmltoimage exit %s (local=%s): %s',
                    exc.returncode,
                    with_local_access,
                    err,
                )
                continue
            else:
                return True
        return False

    def _auto_margin_top_from_header(
        self,
        header_html_path: str,
        orientation: str,
    ) -> str | None:
        """Derive ``margin-top`` from rendered header height (wkhtml stack).

        wkhtmltopdf reserves a fixed band; it does not grow with header HTML.
        Optional keys on ``current_config``:

        - ``auto_header_margin`` (default: on): set ``False`` to skip probing.
        - ``header_margin_padding_mm``: extra space under the header (default 3).
        - ``header_margin_top_min_in`` / ``header_margin_top_max_in``: clamps.
        """
        if self.current_config.get('auto_header_margin') is False:
            return None
        bin_path = self._wkhtmltoimage_bin()
        if not bin_path:
            return None
        width_px = self._page_width_px_for_pdf(orientation)
        dpi = self._pdf_screen_dpi()
        fd, png_name = tempfile.mkstemp(suffix='.png')
        os.close(fd)
        png_path = Path(png_name)
        header_path = Path(header_html_path)
        try:
            if not self._run_wkhtmltoimage(
                bin_path, header_path, png_path, width_px
            ):
                return None
            height_px = self._read_png_pixel_height(png_path)
        except ValueError:
            logger.warning('Header height probe returned an invalid PNG')
            return None
        finally:
            png_path.unlink(missing_ok=True)

        if height_px < 8:
            return None

        padding_mm = float(
            self.current_config.get('header_margin_padding_mm', 3),
        )
        height_in = (height_px / dpi) + (padding_mm / 25.4)
        min_in = float(self.current_config.get('header_margin_top_min_in', 0.35))
        max_in = float(self.current_config.get('header_margin_top_max_in', 3.0))
        height_in = max(min_in, min(max_in, height_in))
        return f'{height_in:.3f}in'

    def _auto_margin_bottom_from_footer(
        self,
        footer_html_path: str,
        orientation: str,
    ) -> str | None:
        """Derive ``margin-bottom`` from rendered footer height (wkhtml stack).

        Optional keys on ``current_config``:

        - ``auto_footer_margin`` (default: on): set ``False`` to skip probing.
        - ``footer_margin_padding_mm``: extra space above the footer (default 0).
        - ``footer_margin_bottom_min_in`` / ``footer_margin_bottom_max_in``: clamps.
        """
        if self.current_config.get('auto_footer_margin') is False:
            return None
        bin_path = self._wkhtmltoimage_bin()
        if not bin_path:
            return None
        width_px = self._page_width_px_for_pdf(orientation)
        dpi = self._pdf_screen_dpi()
        fd, png_name = tempfile.mkstemp(suffix='.png')
        os.close(fd)
        png_path = Path(png_name)
        footer_path = Path(footer_html_path)
        try:
            if not self._run_wkhtmltoimage(
                bin_path, footer_path, png_path, width_px
            ):
                return None
            height_px = self._read_png_pixel_height(png_path)
        except ValueError:
            logger.warning('Footer height probe returned an invalid PNG')
            return None
        finally:
            png_path.unlink(missing_ok=True)

        if height_px < 8:
            return None

        padding_mm = float(
            self.current_config.get('footer_margin_padding_mm', 0),
        )
        height_in = (height_px / dpi) + (padding_mm / 25.4)
        min_in = float(
            self.current_config.get('footer_margin_bottom_min_in', 0.25),
        )
        max_in = float(
            self.current_config.get('footer_margin_bottom_max_in', 3.0),
        )
        height_in = max(min_in, min(max_in, height_in))
        return f'{height_in:.3f}in'

    def _prepare_pdf_options(self) -> dict[str, Any]:
        """Prepare PDF generation options.

        Options are reset from defaults on each run so `--header-html` /
        `--footer-html` and margins from a previous request cannot leak.

        When the page header is off, top margin is reduced (or set via
        ``margin_top`` / ``margin-top`` on ``current_config``). When the
        header is on, ``margin-top`` is inferred from the rendered header
        height unless ``margin_top`` / ``margin-top`` is set in ``current_config``.

        Footer is analogous: ``margin-bottom`` can be sized to the footer
        HTML (``auto_footer_margin``, optional overrides) instead of keeping
        a large default bottom margin.
        """
        self.options = copy.deepcopy(MightyConfig.pdf_options)
        self.options['enable-local-file-access'] = None

        header_on = self.has_option('header_enable')
        footer_on = self.has_option('footer_enable')
        orientation = self.current_config.get('orientation', 'Portrait')

        if header_on:
            header_path = self._build_header_html()
            self.options['--header-html'] = header_path
            margin_top = self._pdf_margin_side_from_config('top')
            if margin_top:
                self.options['margin-top'] = margin_top
            else:
                auto_top = self._auto_margin_top_from_header(
                    header_path, orientation
                )
                if auto_top:
                    self.options['margin-top'] = auto_top
        else:
            self.options.pop('--header-html', None)
            self.options['margin-top'] = (
                self._pdf_margin_side_from_config('top') or '0.30in'
            )

        if footer_on:
            footer_path = self._build_footer_html()
            self.options['--footer-html'] = footer_path
            margin_bottom = self._pdf_margin_side_from_config('bottom')
            if margin_bottom:
                self.options['margin-bottom'] = margin_bottom
            else:
                auto_bottom = self._auto_margin_bottom_from_footer(
                    footer_path, orientation
                )
                if auto_bottom:
                    self.options['margin-bottom'] = auto_bottom
        else:
            self.options.pop('--footer-html', None)
            self.options['margin-bottom'] = (
                self._pdf_margin_side_from_config('bottom') or '0.30in'
            )

        self.options['orientation'] = orientation
        return self.options

    def _inject_font_face_style(self, html_content: str) -> str:
        """Inject configured @font-face rules into HTML head for wkhtmltopdf."""
        fonts: dict[str, str] = {}
        fonts.update(getattr(settings, 'PDFMAKER', {}).get('fonts', {}))
        fonts.update(getattr(settings, 'FONTS_FILES_WEASYPRINT', {}))

        rules: list[str] = []
        for font_file, font_name in fonts.items():
            font_path = find_static_file(f'fonts/{font_file}')
            if not font_path:
                continue
            rules.extend([
                '@font-face {',
                f"  font-family: '{font_name}';",
                f"  src: url('file://{font_path}') format('truetype');",
                '  font-style: normal;',
                '  font-weight: 400;',
                '}',
            ])

        if not rules:
            return html_content

        style_block = '<style>' + '\n'.join(rules) + '</style>'
        if '</head>' in html_content:
            return html_content.replace('</head>', f'{style_block}</head>', 1)
        return style_block + html_content

    def _generate_pdf_file(self, html_content: str) -> str:
        """Generate PDF file from HTML content and return file path."""
        html_content = self._inject_font_face_style(html_content)
        with tempfile.NamedTemporaryFile(
            suffix='.pdf', delete=False
        ) as temp_file:
            temp_file_path = temp_file.name
        pdfkit.from_string(html_content, temp_file_path, options=self.options)
        self.tmp_files.append(temp_file_path)
        return temp_file_path

    def _cleanup_temp_files(self) -> None:
        """Clean up temporary files."""
        for file_path in self.tmp_files:
            try:
                path_obj = Path(file_path)
                if path_obj.exists():
                    path_obj.unlink()
            except (FileNotFoundError, OSError) as error:
                logger.debug(
                    'File already cleaned up: %s - %s', file_path, error
                )
        self.tmp_files.clear()

    def _create_word_response(self, context: Context) -> HttpResponse:
        """Create Word document response."""
        html_content = Template(self.post_data.get('raw_template')).render(
            context
        )
        return self._generate_docx_response(html_content)

    def _generate_docx_response(self, html_content: str) -> HttpResponse:
        """Generate DOCX response from HTML."""
        with tempfile.NamedTemporaryFile(
            suffix='.docx', delete=False
        ) as temp_file:
            output_path = temp_file.name

        pypandoc.convert_text(
            html_content, 'docx', format='html', outputfile=output_path
        )

        docx_data = Path(output_path).read_bytes()
        Path(output_path).unlink(missing_ok=True)

        response = HttpResponse(
            docx_data,
            content_type=(
                'application/vnd.openxmlformats-'
                'officedocument.wordprocessingml.document'
            ),
        )
        docx_filename = self.filename.replace('.pdf', '.docx')
        response['Content-Disposition'] = (
            f'attachment; filename="{docx_filename}"'
        )
        return response

    def _save_pdf(self) -> str:
        """Save PDF and return file path."""
        return self._generate_pdf_file(self.html_content)

    def _create_browser_response(self, pdf_path: str) -> FileResponse:
        """Create browser response for PDF viewing."""
        try:
            # Read the file content into memory since we need to clean up temp files
            pdf_data = Path(pdf_path).read_bytes()
            response = HttpResponse(pdf_data, content_type='application/pdf')
            response['Content-Disposition'] = (
                f'inline; filename="{self.filename}"'
            )
        except (FileNotFoundError, OSError):
            logger.exception('Failed to read PDF file')
            self._cleanup_temp_files()
            raise
        else:
            self._cleanup_temp_files()
            return response

    def _create_download_response(self, pdf_path: str) -> HttpResponse:
        """Create download response for PDF."""
        try:
            pdf_data = Path(pdf_path).read_bytes()
            response = HttpResponse(pdf_data, content_type='application/pdf')
            response['Content-Disposition'] = (
                f'attachment; filename="{self.filename}"'
            )
        except (FileNotFoundError, OSError):
            logger.exception('Failed to read PDF file')
            self._cleanup_temp_files()
            raise
        else:
            self._cleanup_temp_files()
            return response

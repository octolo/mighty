import copy
import json
import logging
import tempfile
from pathlib import Path
from typing import Any, ClassVar

from django.conf import settings
from django.contrib.staticfiles.finders import find as find_static_file
from django.http import FileResponse, HttpResponse
from django.template import Context, Template
from django.template.loader import get_template, select_template

from mighty.apps import MightyConfig
from mighty.filegenerator import (
    build_docx_html_document,
    convert_html_to_docx_bytes,
    render_weasyprint_pdf,
)
from mighty.views.crud import DetailView

logger = logging.getLogger(__name__)


def wrap_editor_html_for_render(content_str: str) -> str:
    """Wrap Froala editor HTML so ``dyntpl`` and Paris timezone apply."""
    return (
        f"{{% load tz dyntpl %}}{{% timezone 'Europe/Paris' %}}"
        f'{content_str or ""}'
        f'{{% endtimezone %}}'
    )


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

    def _build_header_html(self) -> str:
        """Build header HTML if enabled."""
        if self.has_option('header_enable'):
            html = self.render_section(
                self._get_header_template(), self.get_context_data()
            )
            return self._inject_font_face_style(html)
        return ''

    def _build_footer_html(self) -> str:
        """Build footer HTML if enabled."""
        if self.has_option('footer_enable'):
            html = self.render_section(
                self._get_footer_template(), self.get_context_data()
            )
            return self._inject_font_face_style(html)
        return ''

    def _get_header_template(self) -> str:
        """Get header template."""
        return ''

    def _get_footer_template(self) -> str:
        """Get footer template."""
        return ''

    def _prepare_pdf_options(self) -> dict[str, Any]:
        """Prepare WeasyPrint settings and rendered running elements.

        Horizontal margins default to ``MightyConfig.pdf_options``; set
        ``margin_left`` / ``margin-left`` or ``margin_right`` / ``margin-right``
        on ``current_config`` to override (e.g. convocation layout).
        """
        self.options = copy.deepcopy(MightyConfig.pdf_options)
        header_on = self.has_option('header_enable')
        footer_on = self.has_option('footer_enable')
        orientation = self.current_config.get('orientation', 'Portrait')
        self.header_html = self._build_header_html() if header_on else None
        self.footer_html = self._build_footer_html() if footer_on else None
        self.options['margin-top'] = self._pdf_margin_side_from_config(
            'top'
        ) or (
            self.options.get('margin-top', '0.75in') if header_on else '0.30in'
        )
        self.options['margin-bottom'] = self._pdf_margin_side_from_config(
            'bottom'
        ) or (
            self.options.get('margin-bottom', '0.75in')
            if footer_on
            else '0.30in'
        )

        margin_left = self._pdf_margin_side_from_config('left')
        if margin_left:
            self.options['margin-left'] = margin_left

        margin_right = self._pdf_margin_side_from_config('right')
        if margin_right:
            self.options['margin-right'] = margin_right

        self.options['orientation'] = orientation
        return self.options

    def _inject_font_face_style(self, html_content: str) -> str:
        """Inject configured @font-face rules into HTML for WeasyPrint."""
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
        render_weasyprint_pdf(
            html_content,
            output_path=temp_file_path,
            header_html=self.header_html,
            footer_html=self.footer_html,
            options=self.options,
            base_url=str(settings.STATIC_ROOT),
        )
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
        raw = self.post_data.get('raw_template') or ''
        html_content = Template(
            wrap_editor_html_for_render(raw),
        ).render(context)
        return self._generate_docx_response(html_content)

    def _generate_docx_response(self, html_content: str) -> HttpResponse:
        """Generate DOCX response from rendered editor HTML."""
        wrapped_html = build_docx_html_document(html_content)
        docx_data = convert_html_to_docx_bytes(wrapped_html)

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

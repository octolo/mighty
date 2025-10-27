import json
import logging
import tempfile
from pathlib import Path
from typing import Any, ClassVar

import pdfkit
import pypandoc
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
        config_value = self.config.get(key, False)
        return bool(self.request.GET.get(key, config_value))

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
            return self._create_temp_html_file(html)
        return ''

    def _build_footer_html(self) -> str:
        """Build footer HTML if enabled."""
        if self.has_option('footer_enable'):
            html = self.render_section(
                self._get_footer_template(), self.get_context_data()
            )
            return self._create_temp_html_file(html)
        return ''

    def _get_header_template(self) -> str:
        """Get header template."""
        return ''

    def _get_footer_template(self) -> str:
        """Get footer template."""
        return ''

    def _prepare_pdf_options(self) -> dict[str, Any]:
        """Prepare PDF generation options."""
        if self.has_option('header_enable'):
            self.options['--header-html'] = self._build_header_html()
        if self.has_option('footer_enable'):
            self.options['--footer-html'] = self._build_footer_html()
        self.options['orientation'] = self.current_config.get(
            'orientation', 'Portrait'
        )
        return self.options

    def _generate_pdf_file(self, html_content: str) -> str:
        """Generate PDF file from HTML content and return file path."""
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
        """Generate DOCX response from HTML content."""
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

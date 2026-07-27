import datetime
import shutil
from base64 import b64encode
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from mighty.applications.messenger.choices import MODE
from mighty.applications.messenger.reporting import (
    SUMMARY_GROUP_BY,
    company_tag_values,
    generate_missive_report,
    reporting_missive,
    summarize_report,
    summary_header,
    summary_table,
    write_summary_csv,
)
from mighty.applications.messenger.reporting_xlsx import (
    render_company_workbooks,
)


class Command(BaseCommand):
    help = (
        'Generate the missive report, with the same filters as the admin '
        'reporting view. Without --email, the CSV is written in the current '
        'directory instead of being sent.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--since', type=datetime.date.fromisoformat)
        parser.add_argument('--until', type=datetime.date.fromisoformat)
        parser.add_argument(
            '--mode', nargs='+', choices=[mode for mode, _label in MODE]
        )
        parser.add_argument('--email')
        parser.add_argument(
            '--summary',
            nargs='?',
            const=SUMMARY_GROUP_BY,
            metavar='COLUMN',
            help=(
                'Add the totals of the price columns grouped by COLUMN '
                f'(default: {SUMMARY_GROUP_BY}), as a second CSV and, with '
                '--email, in the message body.'
            ),
        )
        parser.add_argument(
            '--template',
            metavar='XLSX',
            help=(
                'Path to an xlsx template to fill with the summary, writing '
                'one workbook per company (zipped in the email). Tags are the '
                'summary column names, written as {{ column }} in any cell.'
            ),
        )
        parser.add_argument(
            '--margin',
            type=float,
            default=0.0,
            metavar='PERCENT',
            help=(
                'Percentage added to the printing costs in the summary; '
                'postage is always passed on at cost.'
            ),
        )

    def handle(self, *args, **options):
        since, until = options['since'], options['until']
        if since and until and since > until:
            raise CommandError('--since cannot be after --until.')
        template = options['template']
        if template and not Path(template).is_file():
            raise CommandError(f'Template not found: {template}.')
        filters = {
            name: options[name]
            for name in ('since', 'until', 'mode')
            if options[name]
        }

        if options['email']:
            reporting_missive(
                options['email'],
                summary=options['summary'],
                template=(
                    b64encode(Path(template).read_bytes()).decode()
                    if template
                    else None
                ),
                margin=options['margin'],
                **filters,
            )
            self.stdout.write(
                self.style.SUCCESS(f'Report sent to {options["email"]}.')
            )
            return

        # ``reporting_missive`` adds the project fields itself; do the same
        # here so both outputs share the exact same columns.
        additional_fields = dict(settings.MISSIVE_REPORTING_ADDITIONAL_FIELDS)
        csvfile = generate_missive_report(
            additional_fields=additional_fields, **filters
        )
        basename = 'reporting_missive_{}'.format(
            datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        )
        shutil.move(csvfile.name, f'{basename}.csv')
        self.stdout.write(
            self.style.SUCCESS(f'Report written to {basename}.csv.')
        )

        if options['summary'] or template:
            self.write_summary(
                f'{basename}.csv',
                basename,
                options['summary'] or SUMMARY_GROUP_BY,
                additional_fields,
                template,
                options['margin'],
            )

    def write_summary(
        self,
        path,
        basename,
        group_by,
        additional_fields,
        template=None,
        margin=0.0,
    ):
        columns, summary = summarize_report(path, group_by, additional_fields)
        table = summary_table(columns, summary, group_by, margin)
        write_summary_csv(table, f'{basename}_summary.csv')
        self.stdout.write(
            self.style.SUCCESS(f'Summary written to {basename}_summary.csv.')
        )
        self.print_table(table)

        if template:
            self.render_workbooks(
                template, basename, columns, summary, group_by, margin
            )

    def render_workbooks(
        self, template, basename, columns, summary, group_by, margin
    ):
        paths, unknown = render_company_workbooks(
            template,
            company_tag_values(columns, summary, group_by, margin),
            f'{basename}_xlsx',
        )
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(
                f'{len(paths)} workbooks written to {basename}_xlsx/.'
            )
        )
        self.stdout.write(
            'Available tags: '
            + ', '.join(
                f'{{{{ {tag} }}}}'
                for tag in summary_header(columns, group_by)
                if tag != 'date'
            )
        )
        if unknown:
            self.stdout.write(
                self.style.WARNING(
                    'Unknown tags left empty: '
                    + ', '.join(f'{{{{ {tag} }}}}' for tag in sorted(unknown))
                )
            )

    def print_table(self, table):
        widths = [max(len(row[i]) for row in table) for i in range(len(table[0]))]
        self.stdout.write('')
        for row in table:
            cells = [row[0].ljust(widths[0])]
            cells.extend(
                value.rjust(width)
                for value, width in zip(row[1:], widths[1:], strict=True)
            )
            self.stdout.write('  '.join(cells))

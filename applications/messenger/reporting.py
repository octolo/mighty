import csv
import ctypes
import gc
import logging
import os
import pathlib
import pickle
import shutil
from base64 import b64decode
from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile, mkdtemp
from typing import NamedTuple

from django.conf import settings
from django.db import reset_queries
from django.utils import timezone
from django.utils.html import escape

from mighty.applications.messenger import choices
from mighty.applications.messenger.reporting_xlsx import (
    render_company_workbooks,
    zip_workbooks,
)
from mighty.functions.facilities import getattr_recursive
from mighty.models import Missive

logger = logging.getLogger(__name__)

fields = [
    'date_send',
    'target',
    'mode',
    'status',
    'type',
    'class',
    'billed_page',
    'external_reference',
    'external_status',
    'color',
]


TRACE_PREFIX = 'trace_json.'

# Missives can carry large ``trace`` blobs, so keep the per-fetch buffer small
# to cap peak memory rather than using the default 2000 rows.
ITER_CHUNK_SIZE = 500

# Final statuses that will never be billed: re-checking them with the provider
# is pointless (and error-prone for failed sends without a partner_id).
NON_BILLABLE_FINAL = {
    choices.STATUS_REJECTED,
    choices.STATUS_CANCELLED,
    choices.STATUS_ERROR,
}

# How often (in rows) memory is released and the progress line is logged.
PROGRESS_LOG_EVERY = 200

# Report column the emailed recap is grouped by, and the one it splits into
# one row per day (the report writes the creation date under ``date_send``).
SUMMARY_GROUP_BY = 'denomination'
SUMMARY_DATE_COLUMN = 'date_send'

# Recap columns computed from the invoiced ones. Postage is passed on at cost,
# so the margin only applies to the printing side.
COLUMN_DISBURSEMENTS = 'debours'
COLUMN_PRINTING = 'total impression'
COLUMN_PRINTING_MARGIN = 'total impression avec marge'
COLUMN_TOTAL = 'total'
COLUMN_TOTAL_MARGIN = 'total avec marge'


class SummaryColumns(NamedTuple):
    postage: list
    printing: list

    @property
    def prices(self):
        return [*self.postage, *self.printing]


def _get_malloc_trim():
    try:
        return ctypes.CDLL('libc.so.6').malloc_trim
    except (OSError, AttributeError):  # not glibc
        return None


MALLOC_TRIM = _get_malloc_trim()


def release_memory():
    """
    Hand freed memory back to the OS.

    Parsing a large trace allocates many times its size, and the allocator
    keeps those pages for reuse afterwards: without this the resident size
    stays at the highest peak reached for the rest of the run.
    """
    gc.collect()
    if MALLOC_TRIM is not None:
        MALLOC_TRIM(0)


def memory_usage_mb():
    """Resident memory of the current process in MiB, ``None`` if unavailable."""
    try:
        with open('/proc/self/statm') as statm:
            resident_pages = int(statm.read().split()[1])
        return resident_pages * os.sysconf('SC_PAGE_SIZE') / (1024 * 1024)
    except (OSError, AttributeError, IndexError, ValueError):
        return None


def log_progress(processed):
    memory = memory_usage_mb()
    logger.info(
        'Missive report: %s rows processed, memory %s',
        processed,
        f'{memory:.1f} MiB' if memory is not None else 'n/a',
    )


def trace_as_dict(missive):
    """
    Read the missive trace as a mapping.

    Failed sends store the raw provider error body, which ``trace_json``
    decodes as ``bytes`` instead of a mapping; ``getattr_recursive`` then
    returns that untraversed blob rather than the requested field.
    """
    trace = missive.trace_json
    return trace if isinstance(trace, dict) else {}


def build_missive_row(missive, additional_fields=None):
    backend = missive.get_backend()

    def trace_path(field_attr):
        path = getattr(backend, field_attr, None)
        if path and path.startswith(TRACE_PREFIX):
            return path[len(TRACE_PREFIX):]
        return None

    # Parse the (potentially large) trace once and read every column from it,
    # instead of letting each backend getter call ``ast.literal_eval`` again.
    trace = trace_as_dict(missive)

    # Only hit the provider (network + save) when the billing data is not
    # already stored on the missive, and when there is a provider reference to
    # ask about: sends that failed before submission never got a partner_id.
    # The billed pages and the invoice come from two different provider calls,
    # so both have to be in the trace before the check can be skipped.
    billing_paths = [
        path
        for path in (
            trace_path('field_billed_page'), trace_path('field_price_infos')
        )
        if path
    ]
    already_billed = bool(billing_paths) and all(
        getattr_recursive(trace, path, default=None, default_on_error=True)
        for path in billing_paths
    )
    if (
        not already_billed
        and missive.partner_id
        and missive.status not in NON_BILLABLE_FINAL
    ):
        try:
            missive.check_status()
        except Exception as e:
            # A provider hiccup must not cost the whole row.
            logger.warning('Cannot check missive %s: %s', missive.id, e)
        trace = trace_as_dict(missive)

    def from_trace(field_attr, getter):
        path = trace_path(field_attr)
        if path:
            return getattr_recursive(
                trace, path, default='', default_on_error=True
            )
        return getter()

    price_infos = backend.get_price_infos()
    row = {
        'date_send': missive.date_create,
        'target': missive.target,
        'mode': missive.mode,
        'status': missive.status,
        'type': from_trace('field_type', backend.get_type),
        'class': from_trace('field_class', backend.get_class),
        'billed_page': from_trace('field_billed_page', backend.get_billed_page),
        'external_reference': from_trace(
            'field_external_reference', backend.get_external_reference
        ),
        'external_status': from_trace(
            'field_external_status', backend.get_external_status
        ),
        'color': from_trace('field_color', backend.get_color),
        **price_infos,
    }

    if additional_fields:
        for field, path in additional_fields.items():
            row[field] = getattr_recursive(
                missive, path, default='', default_on_error=True
            )

    return row


def generate_missive_report(**kwargs):
    """
    Generate a CSV report of missives.

    :param since: only missives created at/after this date
    :param until: only missives created at/before this date
    :param daysoffset: only missives created within the last N days
    :param mode: iterable of modes to filter on
    :param additional_fields: mapping of column name -> attribute path
    """
    # ``html`` (letter body) and ``response`` (raw provider payload) are never
    # read by the report, so avoid loading these potentially large columns.
    missives = Missive.objects.defer('response', 'html')

    if since := kwargs.get('since'):
        missives = missives.filter(date_create__gte=since)

    if until := kwargs.get('until'):
        missives = missives.filter(date_create__lte=until)

    if daysoffset := kwargs.get('daysoffset'):
        until = timezone.now()
        since = until - timedelta(days=daysoffset)
        missives = missives.filter(date_create__range=(since, until))

    if mode := kwargs.get('mode'):
        missives = missives.filter(mode__in=mode)

    additional_fields = kwargs.get('additional_fields')

    # ``additional_fields`` paths usually walk the ``content_object`` generic
    # relation, which is an N+1 source. Let the project declare the optimal
    # prefetch (e.g. a ``GenericPrefetch`` with ``select_related``); otherwise
    # fall back to prefetching the generic relation itself.
    prefetch = getattr(settings, 'MISSIVE_REPORTING_PREFETCH', None)
    if prefetch is None and additional_fields:
        prefetch = ['content_object']
    if prefetch:
        missives = missives.prefetch_related(*prefetch)

    # Spool rows to disk (scalar values only) while collecting the full set of
    # columns, so we never keep the whole queryset nor every row in memory.
    all_fieldnames = set(fields)
    processed = 0
    spool = NamedTemporaryFile(mode='wb', delete=False, suffix='.pkl')
    try:
        for processed, missive in enumerate(
            missives.iterator(chunk_size=ITER_CHUNK_SIZE), start=1
        ):
            try:
                row = build_missive_row(missive, additional_fields)
            except Exception as e:
                logger.warning('Error processing missive %s: %s', missive.id, e)
                continue
            all_fieldnames.update(row.keys())
            pickle.dump(row, spool)
            if not processed % PROGRESS_LOG_EVERY:
                # Under DEBUG, Django keeps the last 9000 queries in memory,
                # parameters included: here that means as many trace blobs.
                reset_queries()
                release_memory()
                log_progress(processed)
        spool.close()
        log_progress(processed)

        ordered_fieldnames = [f for f in fields if f in all_fieldnames]
        ordered_fieldnames.extend(sorted(all_fieldnames - set(fields)))

        csvfile = NamedTemporaryFile(
            mode='w',
            newline='',
            delete=False,
            prefix='missive_report_',
            suffix='.csv',
        )
        writer = csv.DictWriter(csvfile, fieldnames=ordered_fieldnames)
        writer.writeheader()

        with open(spool.name, 'rb') as spooled_rows:
            while True:
                try:
                    writer.writerow(pickle.load(spooled_rows))
                except EOFError:
                    break

        csvfile.close()
        return csvfile
    finally:
        pathlib.Path(spool.name).unlink()


def normalized(column):
    """Invoice labels reach us with erratic spacing and case."""
    return ' '.join(column.split()).casefold()


def split_price_columns(names):
    """Postage columns first, printing ones last, as the recap presents them."""
    printing_labels = {
        normalized(name)
        for name in getattr(settings, 'MISSIVE_REPORTING_PRINTING_COLUMNS', ())
    }
    postage, printing = [], []
    for name in names:
        target = printing if normalized(name) in printing_labels else postage
        target.append(name)
    return SummaryColumns(postage, printing)


def creation_day(value):
    """Local day of a report timestamp, which is stored in UTC."""
    try:
        moment = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return value or 'unknown'
    if timezone.is_aware(moment):
        moment = timezone.localtime(moment)
    return moment.date().isoformat()


def new_totals(columns):
    return {
        'missives': 0,
        'billed_page': 0,
        'prices': dict.fromkeys(columns.prices, 0.0),
    }


def add_totals(totals, data):
    totals['missives'] += data['missives']
    totals['billed_page'] += data['billed_page']
    for column, amount in data['prices'].items():
        totals['prices'][column] += amount


def summarize_report(path, group_by, additional_fields=None):
    """
    Aggregate the billed columns of a generated report.

    Price columns are the ones the backends add from the provider invoice, so
    everything that is neither a standard field nor an additional field.

    :return: the price columns, and per ``group_by`` value and creation day the
        number of missives, the billed pages and the total of each price column
    """
    extra_columns = set(additional_fields or ())
    summary = {}
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        columns = split_price_columns(
            name
            for name in reader.fieldnames
            if name not in fields and name not in extra_columns
        )
        for row in reader:
            key = (
                row.get(group_by) or 'unknown',
                creation_day(row.get(SUMMARY_DATE_COLUMN)),
            )
            group = summary.setdefault(key, new_totals(columns))
            group['missives'] += 1
            try:
                group['billed_page'] += int(float(row['billed_page']))
            except (TypeError, ValueError, KeyError):
                pass
            for column in columns.prices:
                try:
                    group['prices'][column] += float(row[column])
                except (TypeError, ValueError):
                    continue
    return columns, summary


def merge_days(columns, summary):
    """Regroup a per-day summary on its group alone."""
    merged = {}
    for (group, _day), data in summary.items():
        add_totals(merged.setdefault(group, new_totals(columns)), data)
    return merged


def computed_values(data, columns, margin=0.0):
    """The recap columns derived from the invoiced ones."""
    prices = data['prices']
    disbursements = sum(prices[column] for column in columns.postage)
    printing = sum(prices[column] for column in columns.printing)
    with_margin = printing * (1 + margin / 100)
    return {
        COLUMN_DISBURSEMENTS: disbursements,
        COLUMN_PRINTING: printing,
        COLUMN_PRINTING_MARGIN: with_margin,
        COLUMN_TOTAL: disbursements + printing,
        COLUMN_TOTAL_MARGIN: disbursements + with_margin,
    }


def summary_header(columns, group_by):
    return [
        group_by,
        'date',
        'missives',
        *columns.postage,
        COLUMN_DISBURSEMENTS,
        'billed_page',
        *columns.printing,
        COLUMN_PRINTING,
        COLUMN_PRINTING_MARGIN,
        COLUMN_TOTAL,
        COLUMN_TOTAL_MARGIN,
    ]


def summary_row(group, day, data, columns, margin=0.0):
    prices = data['prices']
    computed = computed_values(data, columns, margin)
    return [
        group,
        day,
        str(data['missives']),
        *(f'{prices[column]:.2f}' for column in columns.postage),
        f'{computed[COLUMN_DISBURSEMENTS]:.2f}',
        str(data['billed_page']),
        *(f'{prices[column]:.2f}' for column in columns.printing),
        f'{computed[COLUMN_PRINTING]:.2f}',
        f'{computed[COLUMN_PRINTING_MARGIN]:.2f}',
        f'{computed[COLUMN_TOTAL]:.2f}',
        f'{computed[COLUMN_TOTAL_MARGIN]:.2f}',
    ]


def summary_table(columns, summary, group_by, margin=0.0):
    """Header, one row per group and day, and a total row, all cells strings."""
    totals = new_totals(columns)
    rows = []
    for (group, day), data in sorted(summary.items()):
        add_totals(totals, data)
        rows.append(summary_row(group, day, data, columns, margin))
    rows.append(summary_row('TOTAL', '', totals, columns, margin))
    return [summary_header(columns, group_by), *rows]


def company_tag_values(columns, summary, group_by, margin=0.0):
    """
    Value of every recap column per group, for the xlsx templates.

    A workbook holds a single company, so its days are merged back together.
    """
    values = {}
    for group, data in merge_days(columns, summary).items():
        values[group] = {
            group_by: group,
            'missives': data['missives'],
            'billed_page': data['billed_page'],
            **{
                column: round(data['prices'][column], 2)
                for column in columns.prices
            },
            **{
                column: round(amount, 2)
                for column, amount in computed_values(
                    data, columns, margin
                ).items()
            },
        }
    return values


def write_summary_csv(table, path=None):
    """Write the summary table to ``path``, or to a temporary file."""
    if path is None:
        path = NamedTemporaryFile(
            delete=False, prefix='missive_report_summary_', suffix='.csv'
        ).name
    with open(path, 'w', newline='') as csvfile:
        csv.writer(csvfile).writerows(table)
    return path


def summary_html(table):
    header, *rows = table
    cells = ''.join(f'<th align="left">{escape(cell)}</th>' for cell in header)
    body = ''.join(
        '<tr>{}</tr>'.format(
            ''.join(f'<td align="left">{escape(cell)}</td>' for cell in row)
        )
        for row in rows
    )
    return (
        '<table border="1" cellpadding="4" cellspacing="0">'
        f'<tr>{cells}</tr>{body}</table>'
    )


def reporting_missive(email, summary=None, template=None, margin=0.0, **kwargs):
    """
    Send the report by email.

    :param summary: report column to group the recap by; without it the email
        carries the report alone
    :param template: base64 xlsx template, filled once per group and attached
        as a zip archive; implies a recap
    :param margin: percentage added to the printing costs
    """
    additional_fields = dict(kwargs.pop('additional_fields', {}))
    additional_fields.update(settings.MISSIVE_REPORTING_ADDITIONAL_FIELDS)
    csvfile = generate_missive_report(
        additional_fields=additional_fields, **kwargs
    )
    paths = [csvfile.name]
    html = '<p>Please find the attached report.</p>'
    workbooks = None

    if template and not summary:
        summary = SUMMARY_GROUP_BY

    if summary:
        columns, grouped = summarize_report(
            csvfile.name, summary, additional_fields
        )
        table = summary_table(columns, grouped, summary, margin)
        paths.append(write_summary_csv(table))
        html += summary_html(table)

    if template:
        workbooks = mkdtemp(prefix='missive_report_xlsx_')
        rendered, _unknown = render_company_workbooks(
            b64decode(template),
            company_tag_values(columns, grouped, summary, margin),
            workbooks,
        )
        paths.append(
            zip_workbooks(
                rendered, os.path.join(workbooks, 'missive_report_xlsx.zip')
            )
        )

    missive = Missive(
        mode='EMAIL', target=email, subject='Missive Report', html=html
    )
    attachments = [open(path, 'rb') for path in paths]
    missive.attachments = attachments
    missive.save()
    for attachment in attachments:
        attachment.close()
    for path in paths:
        pathlib.Path(path).unlink()
    if workbooks:
        shutil.rmtree(workbooks, ignore_errors=True)


def task_reporting_missive(email, **kwargs):
    try:
        from .tasks import task_reporting_missive as trm

        return trm.delay(email=email, **kwargs)
    except ImportError:
        # Fallback to the synchronous function if Celery is not available
        reporting_missive(email, **kwargs)

import csv
from datetime import timedelta
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.utils import timezone

from mighty.functions.facilities import getattr_recursive
from mighty.models import Missive

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


def generate_missive_report(**kwargs):
    """
    Generate a CSV report of missives.

    :param missives: QuerySet of Missive objects
    :param file_path: Path to save the CSV file
    :param additional_fields: List of additional fields to include in the report
    """
    missives = Missive.objects.all()

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

    # Collecter d'abord toutes les données pour déterminer tous les champs
    rows = []
    all_fieldnames = set(fields)

    for missive in missives:
        try:
            missive.check_status()
            row = {
                'date_send': missive.date_create,
                'target': missive.target,
                'mode': missive.mode,
                'status': missive.status,
                'type': missive.get_type(),
                'class': missive.get_class(),
                'billed_page': missive.get_billed_page(),
                'external_reference': missive.get_external_reference(),
                'external_status': missive.get_external_status(),
                'color': missive.get_color(),
                **missive.get_price_infos(),
            }
            if additional_fields := kwargs.get('additional_fields'):
                for field, path in additional_fields.items():
                    row[field] = getattr_recursive(
                        missive, path, default='', default_on_error=True
                    )

            # Ajouter tous les champs de cette ligne
            all_fieldnames.update(row.keys())
            rows.append(row)
        except Exception as e:
            print(f'Error processing missive {missive.id}: {e}')

    # Créer la liste ordonnée des champs (fields fixes en premier, puis les dynamiques)
    ordered_fieldnames = [f for f in fields if f in all_fieldnames]
    dynamic_fields = sorted(all_fieldnames - set(fields))
    ordered_fieldnames.extend(dynamic_fields)

    with NamedTemporaryFile(
        mode='w', newline='', delete=False, suffix='.csv'
    ) as tmpfile:
        writer = csv.DictWriter(tmpfile, fieldnames=ordered_fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow(row)

        return tmpfile


def reporting_missive(email, **kwargs):
    additional_fields = kwargs.get('additional_fields', {})
    additional_fields.update(settings.MISSIVE_REPORTING_ADDITIONAL_FIELDS)
    csvfile = generate_missive_report(
        additional_fields=additional_fields, **kwargs
    )
    missive = Missive(
        mode='EMAIL',
        target=email,
        subject='Missive Report',
        html='Please find the attached report.',
    )
    csvfile = open(csvfile.name, 'rb')
    missive.attachments = [csvfile]
    missive.save()
    csvfile.close()


def task_reporting_missive(email, **kwargs):
    try:
        from .tasks import task_reporting_missive as trm

        return trm.delay(email=email, **kwargs)
    except ImportError:
        # Fallback to the synchronous function if Celery is not available
        reporting_missive(email, **kwargs)

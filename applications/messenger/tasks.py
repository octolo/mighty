from celery import shared_task

@shared_task
def task_reporting_missive(email, **kwargs):
    from .reporting import reporting_missive
    reporting_missive(email, **kwargs)

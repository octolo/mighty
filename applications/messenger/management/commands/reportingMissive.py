import csv
import datetime

from mighty.management import ModelBaseCommand
from mighty.models import Missive


class Command(ModelBaseCommand):
    model = Missive
    fields = [
        'uid',
        'mode',
        'subject',
        'status',
        'priority',
        'name',
        'sender',
        'reply',
        'reply_name',
        'target',
        'service',
        'denomination',
        'last_name',
        'first_name',
        'addr_backend_id',
        'address',
        'complement',
        'locality',
        'postal_code',
        'state',
        'state_code',
        'country',
        'country_code',
        'cedex',
        'cedex_code',
        'special',
        'index',
        'raw',
        'msg_id',
        'partner_id',
        'code_error',
        'content_type',
        'object_id',
    ]

    def before_job(self):
        filename = 'reporting_missive_{}.csv'.format(
            datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        )
        self.csvfile = open(filename, 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.csvfile)
        self.writer.writerow([*self.fields, 'pages'])

    def on_object(self, obj):
        data = [getattr(obj, f) for f in self.fields]
        if obj.mode in {'POSTAL', 'POSTALAR'}:
            try:
                documents = obj.check_documents()
                documents = documents.get('documents')
                pages = sum(doc.get('pages_count') for doc in documents)
                data.append(pages)
            except:
                data.append('error')
        else:
            data.append(None)
        self.writer.writerow(data)

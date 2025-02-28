import json


class TableDescriptor:
    def __init__(self, table, request, *args, **kwargs):
        self.table = table(request=request, *args, **kwargs)
        self.table_desc['name'] = self.table.__class__.__name__
        self.generate_desc()

    def as_json(self):
        return json.dumps([
            {
                'name': name,
                'template': getattr(self.Meta.templates, name),
            }
            for name, field in self.form.fields.items()
        ])

import copy, json

class TableDescriptable:
    def __new__(mcs, name, bases, attrs):
        attrs["declared_fields"] = {
            key: attrs.pop(key)
            for key, value in list(attrs.items())
            if isinstance(value, Field)
        }
        new_class = super().__new__(mcs, name, bases, attrs)

        declared_fields = {}
        for base in reversed(new_class.__mro__):
            if hasattr(base, "declared_fields"):
                declared_fields.update(base.declared_fields)

            for attr, value in base.__dict__.items():
                if value is None and attr in declared_fields:
                    declared_fields.pop(attr)
        new_class.base_fields = declared_fields
        new_class.declared_fields = declared_fields
        return new_class

    def __init__(self, field_order=None):
        self.fields = copy.deepcopy(self.base_fields)
        self._bound_fields_cache = {}
        self.order_fields(self.field_order if field_order is None else field_order)

    def order_fields(self, field_order):
        if field_order is None:
            return
        fields = {}
        for key in field_order:
            try:
                fields[key] = self.fields.pop(key)
            except KeyError:  # ignore unknown fields
                pass
        fields.update(self.fields)  # add remaining fields in original order
        self.fields = fields

    def as_json(self):
        return json.dumps([{
            "name": name,
            "template": getattr(self.Meta.templates, name),
        } for name,field in self.form.fields.items()])

    class Meta:
        fields = ()
        ordering = ()
        templates = {}

class TableModelDescriptable(TableDescriptable):
    class Meta(TableDescriptable.Meta):
        model = None

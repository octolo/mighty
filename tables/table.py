import copy, json
from django.forms.models import fields_for_model

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

    def __init__(self, request, field_order=None):
        self.request = requeslt
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

    class Meta:
        fields = ()
        ordering = ()
        templates = {}

class TableModelDescriptor(TableDescriptor):
    class Meta(TableDescriptor.Meta):
        model = None

    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)
        opts = new_class._meta

        if opts.model:
            if opts.fields is None and opts.exclude is None:
                raise ImproperlyConfigured(
                    "Creating a ModelForm without either the 'fields' attribute "
                    "or the 'exclude' attribute is prohibited; form %s "
                    "needs updating." % name
                )
            if opts.fields == ALL_FIELDS:
                opts.fields = None

            fields = fields_for_model(
                opts.model,
                opts.fields,
                opts.exclude,
                opts.widgets,
                opts.formfield_callback,
                opts.localized_fields,
                opts.labels,
                opts.help_texts,
                opts.error_messages,
                opts.field_classes,
            )

            none_model_fields = {k for k, v in fields.items() if not v}
            missing_fields = none_model_fields.difference(new_class.declared_fields)
            if missing_fields:
                message = "Unknown field(s) (%s) specified for %s"
                message = message % (", ".join(missing_fields), opts.model.__name__)
                raise FieldError(message)
                fields.update(new_class.declared_fields)
        else:
            fields = new_class.declared_fields

        new_class.base_fields = fields
        return new_class
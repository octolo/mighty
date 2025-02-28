class FilterDescriptor:
    filters = None

    def __init__(self, filters, *args, **kwargs):
        self.filters = filters

    # def input_type_field(self, field):
    #    return field.widget.input_type

    # def errors_field(self, field):
    #    return field.error_messages

    # def config_field(self, field):
    #    config = {
    #        "required": field.widget.is_required,
    #        "mutlipart": field.widget.needs_multipart_form,
    #    }
    #    if hasattr(field, "min_length"): config["min_length"] = field.min_length
    #    if hasattr(field, "max_length"): config["max_length"] = field.max_length
    #    return config

    # def attrs_field(self, field):
    #    return field.widget.attrs

    # def field_definition(self, field):
    #    return {
    #        "type": self.input_type_field(field),
    #        "errors": self.errors_field(field),
    #        "config": self.config_field(field),
    #        "attrs": self.attrs_field(field),
    #        "help_text": field.help_text,
    #        "label": field.label,
    #    }

    def get_fields(self):
        return {name: self.field_definition(field)
            for name, field in self.form.fields.items()}

    def as_json(self):
        return self.get_fields()

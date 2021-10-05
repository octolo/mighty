class FormDescriptor:
    form = None
    current_field = None
    formats_input = {
        'DATETIME_INPUT_FORMATS': 'datetime',
    }
    request = None
    kwargs = None

    def __init__(self, form, *args, **kwargs):
        self.request = kwargs.get("request")
        self.kwargs = kwargs.get("kwargs")
        self.form = form(request=self.request, kwargs=self.kwargs)

    def input_type_field(self, field):
        if hasattr(field.widget, 'format_key'):
            if field.widget.format_key in self.formats_input:
                return self.formats_input[field.widget.format_key]
        if hasattr(field.widget, 'input_type'):
            return field.widget.input_type
        return field.widget.__class__.__name__.lower()

    def errors_field(self, field):
        return field.error_messages

    def config_field(self, field):
        config = {
            "required": field.required,
            "mutlipart": getattr(field.widget, "needs_multipart_form", False),
        }
        if hasattr(field, 'choices'): config["options"] = self.choices_field(field)
        if hasattr(field, "min_length"): config["min_length"] = field.min_length
        if hasattr(field, "max_length"): config["max_length"] = field.max_length
        if hasattr(field.widget, "allow_multiple_selected"): 
            config["multiselect"] = field.widget.allow_multiple_selected,
        return config

    def attrs_field(self, field):
        return field.widget.attrs

    def choice_label(self, obj, field):
        if hasattr(self.form, self.current_field+"_choices"):
            cfg = getattr(self.form, self.current_field+"_choices")
            return getattr(obj, cfg['option'])

    def choice_value(self, obj, field):
        if hasattr(self.form, self.current_field+"_choices"):
            cfg = getattr(self.form, self.current_field+"_choices")
            return getattr(obj, cfg['value'])

    def choices_field(self, field):
        if hasattr(field.choices, 'queryset'):
            return [{
                "label": self.choice_label(obj, field),
                "value": self.choice_value(obj, field)}
            for obj in field.choices.queryset]
        return [{
                "label": choice[1],
                "value": choice[0]}
            for choice in field.choices]

    def help_text_field(self, field):
        return field.help_text if field.help_text else field.label

    def dependencies_field(self, name):
        return getattr(self.form, "%s_dependencies" % name) if hasattr(self.form, "%s_dependencies" % name) else None
    
    def emptyif_field(self, name):
        return getattr(self.form, "%s_emptyif" % name) if hasattr(self.form, "%s_emptyif" % name) else None

    def name_field(self, name):
        return self.fusion_field(name)

    def fusion_field(self, name):
        if hasattr(self.form, "fusion"):
            for field in self.form.fusion:
                if name in field[1]: return field[0]
        return name
                
    def field_definition(self, field, name):
        self.current_field = name
        config = self.config_field(field)
        config.update(self.attrs_field(field),)
        config.update({
            "name": self.name_field(name),
            "type": self.input_type_field(field),
            "errors": self.errors_field(field),
            "placeholder": self.help_text_field(field),
            "label": field.label,
            "dependencies": self.dependencies_field(name),
            "emptyif": self.emptyif_field(name),
        })
        return config

    def get_fields(self):
        return [self.field_definition(field, name)
            for name,field in self.form.fields.items()]

    def as_json(self):
        return self.get_fields()
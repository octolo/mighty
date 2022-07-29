class FormJsonDescriptor:
    url = None
    form = None
    default_attrs = [
        "label",
        "label_suffix",
        "help_text",
        "required",
        "max_length",
        "min_length",
        "initial",
        "disabled",
        "max_value",
        "min_value",
        "max_digits",
        "decimal_places",
        "allow_empty_file",
    ]

    form_desc = {
        "name": None,
        "action": None,
        "target": "_self",
        "method ": "post",
        "autocomplete": "on",
        "novalidate": False,
        "enctype": "application/x-www-form-urlencoded",
        "rel": None,
        "accept-charset": None,
        "blocks": [],
        "fields": [],
    }

    def __init__(self, form, request, *args, **kwargs):
        self.form = form(request=request, *args, **kwargs)
        self.form_desc["name"] = self.form.__class__.__name__
        self.form_desc["blocks"] = self.form.Options.blocks
        self.generate_desc()

    def generate_desc(self):
        self.form_desc["fields"] = [self.get_field_desc(field, name) for name,field in self.form.fields.items()]

    def get_error_messages(self, field):
        errors = field.error_messages
        for val in field.validators:
            errors.update({val.code: val.message})
        return errors

    def get_input_type(self, field):
        if hasattr(field, 'input_type'):
            return field.input_type
        elif hasattr(field.widget, 'input_type'):
            return field.widget.input_type


    def choice_label(self, obj, field):
        if hasattr(self.form, self.current_field+"_choices"):
            cfg = getattr(self.form, self.current_field+"_choices")
            return getattr(obj, cfg['option'])

    def choice_value(self, obj, field):
        if hasattr(self.form, self.current_field+"_choices"):
            cfg = getattr(self.form, self.current_field+"_choices")
            return getattr(obj, cfg['value'])

    def disable_choice(self, obj, field, choice):
        if hasattr(self.form, self.current_field+"_disable"):
            cfg = getattr(self.form, self.current_field+"_disable")
            return (choice in cfg)

    def get_choices(self, field):
        if hasattr(field, 'choices'):
            #if hasattr(field.choices, 'queryset'):
            #    return [{
            #        "label": self.choice_label(obj, field),
            #        "value": self.choice_value(obj, field),
            #    }
            #    for obj in field.choices.queryset]
            return [{
                    "label": choice[1],
                    "value": choice[0],
                }
                for choice in field.choices]

    def get_dependencies(self, field):
        if field.name in self.form:
            pass

    def get_field_desc(self, field, name):
        desc = {
            "name": name,
            "type": self.get_input_type(field),
            "errors": self.get_error_messages(field),
            "icon": getattr(field, "icon", None),
            "many": getattr(field, "many", False),
            "dict": getattr(field, "dict", None),
            "attrs": getattr(field.widget, "attrs", {}),
            "choices": self.get_choices(field),
            #"dependencies": self.get_dependencies(field),
            #"type": self.get_input_type(field),
        }
        for attr in self.default_attrs: 
            if hasattr(field, attr):
                desc.update({attr: getattr(field, attr)})
        return desc
        #config = self.config_field(field)
        #config.update({
        #    "type": self.input_type_field(field),
        #    "dependencies": self.dependencies_field(name),
        #    "choice_dependencies": self.choice_dependencies_field(name),
        #})
        #return config

    def as_json(self):
        return self.form_desc
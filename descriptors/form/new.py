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

    enctypes = {
        "url": "application/x-www-form-urlencoded",
        "file": "multipart/form-data",
        "text": "text/plain",
    }

    def __init__(self, form, request, *args, **kwargs):
        self.form = form(request=request, *args, **kwargs)
        self.form_desc["name"] = self.form.__class__.__name__
        self.form_desc["blocks"] = getattr(self.form.Options, "blocks", [])
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
        return field.widget.__class__.__name__.lower()

    def option(self, field, name, key):
        if hasattr(field, "Options") and hasattr(field.Options, key):
            return getattr(field.Options, key)
        elif name in self.form.Options.fields:
            return self.form.Options.fields[name][key]
        raise Exception("%s option in error" % name)

    def disable_choice(self, obj, field, choice):
        if hasattr(self.form, self.current_field+"_disable"):
            cfg = getattr(self.form, self.current_field+"_disable")
            return (choice in cfg)

    def get_options(self, field, name):
        if hasattr(field, 'choices'):
            if hasattr(field.choices, 'queryset'):
                print(field.choices.queryset)
                return [{
                    "label": getattr(obj, self.option(field, name, "label")),
                    "value": getattr(obj, self.option(field, name, "value")),
                } for obj in field.choices.queryset]
            return [{
                    "label": choice[1],
                    "value": choice[0],
                } for choice in field.choices]

    def get_dependencies(self, name):
        if name in self.form.Options.dependencies:
            return self.form.Options.dependencies[name]
        return None

    def get_multiple(self, field):
        default = getattr(field, "many", False)
        if hasattr(field, "widget"):
            return getattr(field.widget, "allow_multiple_selected", default)
        return default

    def get_field_desc(self, field, name):
        desc = {
            "name": name,
            "type": self.get_input_type(field),
            "errors": self.get_error_messages(field),
            "icon": getattr(field, "icon", None),
            "multiple": self.get_multiple(field),
            "dict": getattr(field, "dict", None),
            "attrs": getattr(field.widget, "attrs", {}),
            "options": self.get_options(field, name),
            "dependencies": self.get_dependencies(name),
        }
        for attr in self.default_attrs: 
            if hasattr(field, attr):
                desc.update({attr: getattr(field, attr)})
        return desc

    def as_json(self):
        return self.form_desc
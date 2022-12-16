from django.urls import reverse

class FormDescriptor:
    url = None
    form = None
    as_type = {
        "datefield": "date",
        "datetimefield": "datetime",
        "colorwidget": "color",
    }
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
        "fclass",
        "lclass",
        "mode",
        "create_if_not_exist",
        "api",
        "preference",
        "fast_create",
        "form_create",
        "post_create",
        "field_detail",
        "discriminant",
    ]
    url_attrs = [
        "form_create_url",
        "post_create_url",
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
        if "drf_kwargs" in kwargs: self.drf_kwargs = kwargs.get("drf_kwargs")
        print(self.drf_kwargs)
        self.form = form(request=request, *args, **kwargs)
        self.form_desc["name"] = str(self.form.__class__.__name__).lower()
        self.form_desc["blocks"] = getattr(self.form.Options, "blocks", [])
        self.generate_desc()

    def generate_desc(self):
        self.form_desc["fields"] = [self.get_field_desc(field, name) for name,field in self.form.fields.items()]

    def get_error_messages(self, field):
        errors = field.error_messages
        for val in field.validators:
            if hasattr(val, "code"):
                errors.update({val.code: val.message})
            else:
                errors.update({"nocode": val.messages})
        return errors

    def check_enctype(self, desc):
        if desc["type"] in ("file", "image"):
            self.form_desc["enctype"] = self.enctypes["file"]

    def get_input_type(self, field):
        if hasattr(field, 'input_type'):
            return field.input_type
        elif hasattr(field, "widget"): 
            if hasattr(field.widget, 'input_type'):
                return field.widget.input_type
            wtype = field.widget.__class__.__name__.lower()
            return self.as_type[wtype] if wtype in self.as_type else wtype
        ftype = field.__class__.__name__.lower()
        return self.as_type[ftype] if ftype in self.as_type else ftype

    def get_input_type_text(self, field):
        base_type = self.get_input_type(field)
        if base_type == "text":
            ftype = field.__class__.__name__.lower()
            if ftype in self.as_type:
                return self.as_type[ftype]
            if field.widget:
                ftype = field.widget.__class__.__name__.lower()
                if ftype in self.as_type:
                    return self.as_type[ftype]
        return base_type

    def option(self, field, name, key, default=None):
        if name in self.form.Options.fields and key in self.form.Options.fields[name]:
            return self.form.Options.fields[name][key]
        elif hasattr(field, "Options") and hasattr(field.Options, key) and getattr(field.Options, key):
            return getattr(field.Options, key)
        if default: return default
        raise Exception("%s option in error" % name)

    def disable_choice(self, obj, field, choice):
        if hasattr(self.form, self.current_field+"_disable"):
            cfg = getattr(self.form, self.current_field+"_disable")
            return (choice in cfg)

    def get_options(self, field, name):
        if hasattr(field, 'choices'):
            if self.get_api(field, name):
                return []
            elif hasattr(field.choices, 'queryset'):
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

    def get_api(self, field, name):
        try:
            return self.option(field, name, "api")
        except Exception:
            return None

    def url_arg(self, arg):
        try:
            return self.request.kwargs[arg]
        except Exception:
            return self.drf_kwargs[arg]

    def kwargs_split(self, arg):
        arg = arg.split(":")
        if len(arg) > 1:
            if arg[0] == "url": return self.url_arg(arg[1])
            return None
        return arg[0]

    def get_url_attr(self, field, name, attr):
        try:
            config = self.option(field, name, attr)
            return reverse(config["name"], kwargs={k: self.kwargs_split(v) for k,v in config["kwargs"].items()})
        except Exception:
            return None

    def get_field_detail(self, field, name):
        return self.option(field, name, "field_detail", name+"_detail")

    def get_field_desc(self, field, name):
        desc = {
            "name": name,
            "type": self.get_input_type(field),
            "type_text": self.get_input_type_text(field),
            "errors": self.get_error_messages(field),
            "icon": getattr(field, "icon", None),
            "multiple": self.get_multiple(field),
            "isobj": getattr(field, "isobj", None),
            "attrs": getattr(field.widget, "attrs", {}),
            "options": self.get_options(field, name),
            "dependencies": self.get_dependencies(name),
        }
        if (hasattr(field, 'choices') and hasattr(field.choices, 'queryset')) or self.get_api(field, name):
            desc.update({
                "opt_label": self.option(field, name, "label"),
                "opt_value": self.option(field, name, "value"),
            })
        for attr in self.default_attrs:
            if hasattr(self, "get_%s"%attr):
                desc.update({attr: getattr(self, "get_%s"%attr)(field, name)})
            elif hasattr(field, attr):
                desc.update({attr: getattr(field, attr)})
            else:
                try:
                    desc.update({attr: self.option(field, name, attr)})
                except Exception:
                    pass
        for attr in self.url_attrs:
            desc.update({attr: self.get_url_attr(field, name, attr)})
        self.check_enctype(desc)
        return desc

    def as_json(self):
        return self.form_desc
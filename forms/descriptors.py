from django.urls import reverse
from django import forms
import json

form_init_fields = (
    "data",
    "files",
    "auto_id",
    "prefix",
    "initial",
    "error_class",
    "label_suffix",
    "empty_permitted",
    "use_required_attribute",
    "renderer")

class FormShare:
    additional_fields = []
    additional_fields_options = {}

    def get_sub_form(self, form, *args, **kwargs):
        from mighty.forms.descriptors import FormDescriptor
        return json.loads(json.dumps(FormDescriptor(form, self.request).as_json()))

    def add_addtionnal_field(self, field, options=None):
        self.additional_fields.append(field)
        if options:
            self.additional_fields_options[field] = options

    def reset_additional_fields(self):
        self.additional_fields = []
        self.additional_fields_options = {}

    def prepare_descriptor(self, *args, **kwargs): pass

class FormDescriptable(FormShare, forms.Form):
    request = None

    class Options:
        dependencies = {}
        fields = {}
        url = None
        blocks = None

    def form_init(self, kwargs):
        list_fields = form_init_fields + ("field_order",)
        return {f: kwargs[f] for f in kwargs if f in list_fields}

    def __init__(self, *args, **kwargs):
        self.reset_additional_fields()
        self.request = kwargs.pop("request") if "request" in kwargs else None
        super(forms.Form, self).__init__(*args, **{f: kwargs[f] for f in self.form_init(kwargs)})
        self.prepare_descriptor(*args, **kwargs)

class ModelFormDescriptable(FormShare, forms.ModelForm):
    request = None

    class Options:
        dependencies = {}
        fields = {}
        url = None
        blocks = None

    def form_init(self, kwargs):
        list_fields = form_init_fields + ("instance",)
        return {f: kwargs[f] for f in kwargs if f in list_fields}

    def __init__(self, *args, **kwargs):
        self.reset_additional_fields()
        self.request = kwargs.pop("request") if "request" in kwargs else None
        super(forms.ModelForm, self).__init__(*args, **{f: kwargs.get(f) for f in self.form_init(kwargs)})
        self.prepare_descriptor(*args, **kwargs)

class FormDescriptor:
    url = None
    form = None
    obj = None
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
        "form_edit",
        "post_create",
        "field_detail",
        "discriminant",
        "apipayload",
        "filter",
        "splitted",
        "splitted_refs",
        "vars_url",
        "raw_field",
        "raw_method",
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
        "additional_fields": [],
    }

    enctypes = {
        "url": "application/x-www-form-urlencoded",
        "file": "multipart/form-data",
        "text": "text/plain",
    }

    def __init__(self, form, request, *args, **kwargs):
        if "drf_kwargs" in kwargs: self.drf_kwargs = kwargs.get("drf_kwargs")
        self.form = form(request=request, *args, **kwargs)
        self.form_desc["name"] = str(self.form.__class__.__name__).lower()

        self.form_desc["blocks"] = getattr(self.form.Options, "blocks", [])

        self.form_desc["additional_fields"] = self.form.additional_fields

        self.obj = kwargs.get("obj")
        self.generate_desc()

    def generate_desc(self):
        self.form_desc["fields"] = [self.get_field_desc(field, name) for name,field in self.form.fields.items()]

    def get_error_messages(self, field):
        errors = {k: str(v) for k,v in field.error_messages.items()}
        for val in field.validators:
            if hasattr(val, "code"):
                errors.update({val.code: str(val.message)})
            else:
                errors.update({"nocode": [str(msg) for msg in val.messages]})
        return errors

    def check_enctype(self, desc):
        if desc["type"] in ("file", "image"):
            self.form_desc["enctype"] = self.enctypes["file"]

    def get_input_type(self, field, name):
        if hasattr(field, 'input_type'):
            return field.input_type
        elif hasattr(field, "widget"):
            if hasattr(field.widget, 'input_type'):
                return self.option(field, name, "input_type", field.widget.input_type)
            wtype = field.widget.__class__.__name__.lower()
            return self.as_type[wtype] if wtype in self.as_type else self.option(field, name, "input_type", wtype)
        ftype = field.__class__.__name__.lower()
        return self.as_type[ftype] if ftype in self.as_type else self.option(field, name, "input_type")

    def get_input_type_text(self, field, name):
        base_type = self.get_input_type(field, name)
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
        additional_options = self.form.additional_fields_options
        if name in self.form.Options.fields and key in self.form.Options.fields[name]:
            return self.form.Options.fields[name][key]
        elif name in additional_options and key in additional_options[name]:
            return additional_options[name][key]
        elif hasattr(field, "Options") and hasattr(field.Options, key):
            return getattr(field.Options, key)
        return default

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
                    "label": str(getattr(obj, self.option(field, name, "label"))),
                    "value": getattr(obj, self.option(field, name, "value")),
                } for obj in field.choices.queryset]
            return [{
                    "label": str(choice[1]),
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

    def get_initial_value(self, field, name):
        return self.option(field, name, "initial", field.initial)


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

    def get_label(self, field, name):
        return str(getattr(field, "label"))

    def get_field_desc(self, field, name):
        desc = {
            "name": name,
            "type":  self.option(field, name, "input_type", self.get_input_type(field, name)),
            "type_text": self.get_input_type_text(field, name),
            "errors": self.get_error_messages(field),
            "icon": self.option(field, name, "icon"),
            "multiple": self.get_multiple(field),
            "isobj": getattr(field, "isobj", None),
            "attrs": getattr(field.widget, "attrs", {}),
            "options": self.get_options(field, name),
            "dependencies": self.get_dependencies(name),
            "initial": self.get_initial_value(field, name),
            "config": self.option(field, name, "config"),
            "exclude": self.option(field, name, "exclude"),
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

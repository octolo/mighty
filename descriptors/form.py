class FormDescriptor:
    form = None
    current_field = None
    formats_input = {
        "DATETIME_INPUT_FORMATS": "datetime",
        "datefield": "date",
        "tel": "phone"
    }
    default_icon = {
        "email": "at",
        "datetime": "calendar",
        "date": "calendar",
        "password": "key",
        "file": "file-upload",
        "phone": "mobile-alt",
    }
    validators = {
        "regexvalidator": ("code", "message", "pattern")
    }

    def __init__(self, form, request, *args, **kwargs):
        self.form = form(request=request, *args, **kwargs)

    def input_type_field(self, field):
        if hasattr(field, "input_type"):
            return field.input_type
        if hasattr(field.widget, 'format_key'):
            if field.widget.format_key in self.formats_input:
                return self.formats_input[field.widget.format_key]
        if hasattr(field.widget, 'input_type'):
            return self.formats_input.get(field.widget.input_type, field.widget.input_type)
        return self.formats_input.get(field.widget.__class__.__name__.lower(), field.widget.__class__.__name__.lower()) 

    def config_field(self, field):
        config = {
            "required": field.required,
            "mutlipart": getattr(field.widget, "needs_multipart_form", False),
        }
        if hasattr(field, 'choices'): config["options"] = self.choices_field(field)
        if hasattr(field, 'choices_enhanced'): config["options_enhanced"] = self.choices_field(field)
        if hasattr(field, "min_length"): config["min_length"] = field.min_length
        if hasattr(field, "max_length"): config["max_length"] = field.max_length
        if hasattr(field.widget, "allow_multiple_selected"): 
            config["multiselect"] = field.widget.allow_multiple_selected,
        return config

    def defaultIcon_field(self, field):
        return self.default_icon.get(self.input_type_field(field), None)

    def as_json(self): return self.get_fields()
    def many_field(self, field): return field.many if hasattr(field, "many") else False
    def isObj_field(self, field): return field.isObj if hasattr(field, "isObj") else None
    def isArray_field(self, field): return field.isArray if hasattr(field, "isArray") else None
    def errors_field(self, field): return field.error_messages
    def attrs_field(self, field): return getattr(field.widget, "attrs", {})
    def name_field(self, name): return self.fusion_field(name)
    def help_text_field(self, field): return field.help_text if field.help_text else field.label
    def hasIcon_field(self, field): return field.icon if hasattr(field, "icon") else self.defaultIcon_field(field)

    def regexvalidator_pattern(self, field, validator):
        return validator.regex.pattern

    def get_config_validator(self, val, field, validator):
        name = "%s_%s" % (validator.__class__.__name__.lower(), val)
        if hasattr(self, name):
            return getattr(self, name)(field, validator)
        return getattr(validator, val)

    def config_validator(self, field, validator):
        name = validator.__class__.__name__.lower()
        if name in self.validators:
            config = {"name": name}
            config.update({val: self.get_config_validator(val, field, validator) 
                for val in self.validators[name]})
            return config
        return False

    def validators_fields(self, field):
        if len(field.validators):
            validators = [self.config_validator(field, validator)
                for validator in field.validators]
            return [val for val in validators if val]

    def dependencies_field(self, name):
        return getattr(self.form, "%s_dependencies" % name) if hasattr(self.form, "%s_dependencies" % name) else None
    
    def choice_dependencies_field(self, name):
        return getattr(self.form, "%s_choice_dependencies" % name) if hasattr(self.form, "%s_choice_dependencies" % name) else None

    def emptyif_field(self, name):
        return getattr(self.form, "%s_emptyif" % name) if hasattr(self.form, "%s_emptyif" % name) else None

    def get_fields(self):
        return [self.field_definition(field, name)
            for name,field in self.form.fields.items()]

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

    def choices_field(self, field):
        if hasattr(field.choices, 'queryset'):
            return [{
                "label": self.choice_label(obj, field),
                "value": self.choice_value(obj, field),
                "disable": self.disable_choice(obj, field),
            }
            for obj in field.choices.queryset]
        return [{
                "label": choice[1],
                "value": choice[0],
                "disable": self.disable_choice(choice, field, choice[0]),
            }
            for choice in field.choices]

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
            "validators": self.validators_fields(field),
            "label": field.label,
            "dependencies": self.dependencies_field(name),
            "choice_dependencies": self.choice_dependencies_field(name),
            "emptyif": self.emptyif_field(name),
            "many": self.many_field(field),
            "isObj": self.isObj_field(field),
            "isArray": self.isArray_field(field),
            "icon": self.hasIcon_field(field),
        })
        return config


from django.template import Context, Template


def EnableVariableEditorModel(**kwargs):
    def wrapper(obj):
        from mighty.models import TemplateVariable

        class NewClass(obj):
            eve_variable_to_match = kwargs.get('to_match', 'vhtml_')
            eve_variable_fields = kwargs.get('fields', [])
            eve_variable_list = []
            eve_variable_related = {}
            eve_variable_prefix = kwargs.get('prefix', '')

            class Meta(obj.Meta):
                abstract = True

            """
            " PROPERTIES
            """

            # Check if model use template variables
            @property
            def has_eve_variable_template(self):
                return (
                    len(self.eve_variable_template)
                    if hasattr(self, 'eve_variable_template')
                    else False
                )

            # Directory template html
            @property
            def eve_dir_variables_or_none(self):
                return (
                    self.eve_dir_variables
                    if hasattr(self, 'eve_dir_variables')
                    else 'variables/'
                )

            # Context template html
            @property
            def eve_context_or_none(self):
                return self.eve_context if hasattr(self, 'eve_context') else {}

            # Get all template variable model
            @property
            def eve_template_variable_qs(self):
                return TemplateVariable.objects.filter(
                    content_type=self.get_content_type(), hidden=False
                )

            def eve_template_variable_qs_version(self, version=1):
                qs = []
                for tvar in self.eve_template_variable_qs.filter(
                    version=version
                ):
                    tvar.context = self.eve_context_or_none
                    qs.append(tvar)
                return qs

            # Return qs template variable model
            @property
            def eve_tv(self):
                return {
                    tvar.name: self.eve_get_template_variable_compiled(
                        tvar.template
                    )
                    for tvar in self.eve_template_variable_qs_version()
                }

            @property
            def eve_tv2(self):
                return {
                    tvar.name: tvar
                    for tvar in self.eve_template_variable_qs_version(2)
                }

            # Json desc from template variable model
            @property
            def eve_template_variable_list(self):
                return [
                    tvar.json_object for tvar in self.eve_template_variable_qs
                ]

            # Prefix variable
            @property
            def eve_ev_tv_prefix(self):
                return self.eve_variable_prefix + 'eve_tv.'

            """
            " METHODS
            """

            # Return variable with prefix
            def eve_get_variable_prefix(self, f):
                return self.eve_ev_tv_prefix + f

            # Add a wrapper html (date, extends...)
            def eve_wrapper_or_none(self, tpl):
                if hasattr(self, 'eve_wrapper'):
                    wrp = self.eve_wrapper.split('{{ content }}')
                    return wrp[0] + tpl + wrp[1]
                return tpl

            # Create template variable if does not exist
            def eve_create_template_variable(self):
                if hasattr(self, 'eve_variable_template'):
                    for tv in self.eve_variable_template:
                        self.eve_get_template_variable(tv)

            # Get or create template if not exist
            def eve_get_template_variable(self, name):
                try:
                    tvar = TemplateVariable.objects.get(
                        name=name, content_type=self.get_content_type()
                    )
                    return self.eve_get_template_variable_compiled(
                        tvar.template
                    )
                except TemplateVariable.DoesNotExist:
                    from django.template.loader import get_template

                    tvar = get_template(
                        self.eve_dir_variables_or_none + name + '.html'
                    ).template.source
                    tvar_tosave = TemplateVariable(
                        name=name,
                        template=tvar,
                        content_type=self.get_content_type(),
                    )
                    tvar_tosave.save()
                    return self.eve_get_template_variable_compiled(tvar)

            # Get template compiled with context
            def eve_get_template_variable_compiled(self, tpl):
                return Template(self.eve_wrapper_or_none(tpl)).render(
                    Context(self.eve_context_or_none)
                )

            # Add var template in list
            def eve_add_template_variable(self):
                self.eve_variable_list += self.eve_template_variable_list

            # Return list of matching variable python
            def eve_prefix_match_list(self):
                return [
                    i
                    for i in list(dir(self))
                    if self.eve_variable_to_match in i
                ]

            def eve_key_or_default(self, f, key):
                return (
                    getattr(getattr(self, f), key)
                    if hasattr(getattr(self, f), key)
                    else f.replace(self.eve_variable_to_match, '')
                )

            def eve_vn_or_default(self, f):
                try:
                    return getattr(type(self), f).field.verbose_name
                except:
                    return f

            def eve_add_variable_prefix(self):
                for f in self.eve_prefix_match_list():
                    self.eve_variable_list.append({
                        'var': self.eve_variable_prefix + f,
                        'desc': self.eve_key_or_default(f, 'desc'),
                    })

            def eve_add_variable_fields(self):
                for f in self.eve_variable_fields:
                    self.eve_variable_list.append({
                        'var': self.eve_get_variable_prefix(f),
                        'desc': self.eve_vn_or_default(f),
                    })

            def eve_add_variable_related(self):
                for k, f in self.eve_variable_related.items():
                    self.eve_variable_list += f().eve_variable_prefixed_list(
                        prefix=k
                    )

            def eve_variable_prefixed_list(self, **kwargs):
                self.eve_variable_related = kwargs.get('related', {})
                self.eve_variable_list = []
                self.eve_add_variable_fields()
                self.eve_add_variable_related()
                self.eve_add_variable_prefix()
                self.eve_add_template_variable()
                return self.eve_variable_list

        NewClass.__name__ = obj.__name__
        return NewClass

    return wrapper

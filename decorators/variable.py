def EnableVariableEditorModel(**kwargs):
    def wrapper(obj):
        class Prop(obj):    
            variable_to_match = kwargs.get("to_match", "vhtml_")
            variable_fields = kwargs.get("fields", [])
            variable_list = []
            variable_related = {}
            variable_prefix = None

            class Meta(obj.Meta):
                abstract = True

            def c_list(self) -> list[str]:
                prop_list = [p for p in dir(self)]
                _list = []

                for i in prop_list:
                    if self.variable_to_match in i:
                        _list.append(i)

                return _list
            
            def key_or_default(self, f, key):
                if hasattr(getattr(self, f), key):
                    return getattr(getattr(self, f), key)
                return f.replace(self.variable_to_match, "")

            def vn_or_default(self, f):
                try:
                    return getattr(type(self), f).field.verbose_name
                except:
                    return f

            def get_variable_prefix(self, f):
                return self.variable_prefix+"."+f if self.variable_prefix else f
                


            def add_variable_prefix(self):
                f_list = self.c_list()
                prefix = self.variable_prefix
                for f in f_list:
                    try:
                        self.variable_list.append({
                            "var": self.get_variable_prefix(f),
                            "desc": self.key_or_default(f, "desc"),
                        })
                    except:
                        pass

            def add_variable_fields(self):
                for f in self.variable_fields:
                    self.variable_list.append({
                        "var": self.get_variable_prefix(f),
                        "desc": self.vn_or_default(f),
                    })

            def add_variable_related(self):
                for k,f in self.variable_related.items():
                    self.variable_list += f().v_list(prefix=k)

            def v_list(self, **kwargs):
                self.variable_related = kwargs.get("related", {})
                self.variable_prefix = kwargs.get("prefix")
                self.variable_list = []
                self.add_variable_fields()
                self.add_variable_related()
                self.add_variable_prefix()
                return self.variable_list


        return Prop
    return wrapper

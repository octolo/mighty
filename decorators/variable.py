def EnableVariableEditorModel(**kwargs):
    def wrapper(obj):
        class Prop(obj):    
            class Meta(obj.Meta):
                abstract = True

            def c_list(self) -> list[str]:
                prop_list = [p for p in dir(self)]
                _list = []

                for i in prop_list:
                    if kwargs.get("to_match") in i:
                        _list.append(i)

                return _list
            
            def v_list(self) -> list[str]:
                f_list = self.c_list()
                _list = []

                if kwargs.get("lookup_list") == True:
                    for f in f_list:
                        try:
                            _list.append({
                                "var": f, 
                                "desc": getattr(getattr(self, f), "desc"),
                                "editor": getattr(getattr(self, f), "editor"),
                            })
                        except:
                            pass

                return _list
        return Prop
    return wrapper

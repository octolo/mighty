def EnableVariableEditorModel(**kwargs):
    def wrapper(_class):
        class Prop(_class):
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
                            _var = getattr(getattr(self, f), "var")
                        except:
                            _var = None
                        try:
                            _desc = getattr(getattr(self, f), "desc")
                        except:
                            _desc = None
                        try:
                            _editor = getattr(getattr(self, f), "editor")
                        except:
                            _editor = None

                        _list.append({
                            "var": _var, 
                            "desc": _desc,
                            "editor": _editor,
                        })

                return _list
        return Prop
    return wrapper

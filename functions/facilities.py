def getattr_recursive(obj, strtoget, split='.', default=None, default_on_error=None):
    if strtoget:
        keys = strtoget.split(split)
        current = obj
        try:
            for key in keys:
                if isinstance(current, dict):  # Si c'est un dictionnaire
                    current = current[key]
                elif hasattr(current, key):  # Si c'est une classe avec l'attribut
                    current = getattr(current, key)
                elif key.isdigit(): # Si c'est une liste
                    try:
                        current = current[key]
                    except TypeError:
                        idx = int(key)
                        current = current[idx] if idx < len(current) else None
            return current
        except (KeyError, AttributeError, TypeError):
            if default_on_error is not None:
                return default
            pass
    return default

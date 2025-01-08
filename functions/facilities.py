def getattr_recursive(obj, strtoget, split=".", default=None):
    if strtoget:
        keys = strtoget.split(split)
        current = obj
        try:
            for key in keys:
                if isinstance(current, dict):  # Si c'est un dictionnaire
                    current = current[key]
                elif hasattr(current, key):    # Si c'est une classe avec l'attribut
                    current = getattr(current, key)
            return current
        except (KeyError, AttributeError, TypeError):
            pass
    return default

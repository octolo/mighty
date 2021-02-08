default_app_config = 'mighty.applications.shop.apps.ShopConfig'
from mighty.functions import key, get_model

def generate_code_type():
    code = key(8, string.ascii_letters+string.hexdigits).upper()
    try:
        get_model('mighty', 'Discount').objects.get(code=code)
        return generate_code_type(model)
    except ObjectDoesNotExist:
        return code
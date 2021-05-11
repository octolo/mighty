default_app_config = 'mighty.applications.shop.apps.ShopConfig'
from django.core.exceptions import ObjectDoesNotExist
from mighty.functions import key, get_model
import string

def generate_code_type():
    code = key(8, string.ascii_letters+string.hexdigits).upper()
    try:
        get_model('mighty', 'Discount').objects.get(code=code)
        return generate_code_type(model)
    except ObjectDoesNotExist:
        return code
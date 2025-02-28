default_app_config = 'mighty.applications.shop.apps.ShopConfig'
import string

from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist

from mighty.functions import get_model, key


def generate_code_type():
    code = key(8, string.ascii_letters + string.hexdigits).upper()
    try:
        Model = get_model('mighty', 'Discount')
        Model._meta.get_field('code')
        Model.objects.get(code=code)
        return generate_code_offer()
        return generate_code_type()
    except ObjectDoesNotExist:
        return code
    except FieldDoesNotExist:
        return code


def generate_code_service():
    code = key(8, string.ascii_letters + string.hexdigits).upper()
    try:
        Model = get_model('mighty', 'Service')
        Model._meta.get_field('code')
        Model.objects.get(code=code)
        return generate_code_service()
    except ObjectDoesNotExist:
        return code
    except FieldDoesNotExist:
        return code


def generate_code_offer():
    return key(8, string.ascii_letters + string.hexdigits).upper()
    # try:
    #    Model = get_model('mighty', 'Offer')
    #    Model._meta.get_field('code')
    #    Model.objects.get(code=code)
    #    return generate_code_offer()
    # except FieldDoesNotExist:
    #    return code
    # except ObjectDoesNotExist:
    #    return code

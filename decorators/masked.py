from collections import OrderedDict

from mighty.functions import mask


def maskedSerializer(except_mask=(), full_mask=()):
    def deco(cls):
        cls.except_mask = except_mask
        cls.full_mask = full_mask

        class Masked(cls):
            mask_enable = False

            def mask(cls, field, value):
                return mask(value, 0) if field in cls.full_mask else mask(value)

            def mask_dict(cls, field, value):
                if isinstance(value, (bool, type(None))):
                    return False
                if isinstance(value, (list, OrderedDict, dict)):
                    return cls.mask_field(field, value)
                return cls.mask(field, value)

            def mask_field(cls, field, value):
                if field in cls.except_mask:
                    return (field, value)
                if isinstance(value, (bool, type(None))):
                    return (field, False)
                if isinstance(value, dict):
                    return (field, {f: cls.mask_dict(f, v) for f, v in value.items()})
                if isinstance(value, (list, OrderedDict)):
                    return (field, value)
                return (field, cls.mask(field, value))

            def to_representation(cls, instance):
                if hasattr(cls.parent, 'context') and hasattr(cls._context, 'mask_enable'):
                    cls._context['mask_enable'] = cls.parent.context['mask_enable']
                ret = super().to_representation(instance)
                if cls._context.get('mask_enable', False):
                    return OrderedDict([cls.mask_field(field, ret[field]) for field in ret])
                return ret

        return Masked
    return deco


def maskedView(masked_for=()):
    def deco(cls):
        cls.masked_for = masked_for

        class Masked(cls):
            need_tobe_masked = True

            def check_permissions(cls, request):
                try:
                    super().check_permissions(request)
                    cls.need_tobe_masked = False
                except Exception as e:
                    if isinstance(e, cls.masked_for):
                        cls.need_tobe_masked = True
                    else:
                        raise e

            def get_serializer_context(cls):
                context = super().get_serializer_context()
                context.update({'mask_enable': cls.need_tobe_masked})
                return context

        return Masked
    return deco

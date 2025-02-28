from collections import OrderedDict

from mighty.functions import mask


def maskedSerializer(except_mask=(), full_mask=()):
    def deco(cls):
        cls.except_mask = except_mask
        cls.full_mask = full_mask

        class Masked(cls):
            mask_enable = False

            def mask(self, field, value):
                return mask(value, 0) if field in self.full_mask else mask(value)

            def mask_dict(self, field, value):
                if isinstance(value, bool | type(None)):
                    return False
                if isinstance(value, list | OrderedDict | dict):
                    return self.mask_field(field, value)
                return self.mask(field, value)

            def mask_field(self, field, value):
                if field in self.except_mask:
                    return (field, value)
                if isinstance(value, bool | type(None)):
                    return (field, False)
                if isinstance(value, dict):
                    return (field, {f: self.mask_dict(f, v) for f, v in value.items()})
                if isinstance(value, list | OrderedDict):
                    return (field, value)
                return (field, self.mask(field, value))

            def to_representation(self, instance):
                if hasattr(self.parent, 'context') and hasattr(self._context, 'mask_enable'):
                    self._context['mask_enable'] = self.parent.context['mask_enable']
                ret = super().to_representation(instance)
                if self._context.get('mask_enable', False):
                    return OrderedDict([self.mask_field(field, ret[field]) for field in ret])
                return ret

        return Masked
    return deco


def maskedView(masked_for=()):
    def deco(cls):
        cls.masked_for = masked_for

        class Masked(cls):
            need_tobe_masked = True

            def check_permissions(self, request):
                try:
                    super().check_permissions(request)
                    self.need_tobe_masked = False
                except Exception as e:
                    if isinstance(e, self.masked_for):
                        self.need_tobe_masked = True
                    else:
                        raise

            def get_serializer_context(self):
                context = super().get_serializer_context()
                context.update({'mask_enable': self.need_tobe_masked})
                return context

        return Masked
    return deco

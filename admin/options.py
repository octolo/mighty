from django.contrib.auth import get_permission_codename


def has_disable_permission(self, request, obj=None):
    opts = self.opts
    codename = get_permission_codename('disable', opts)
    return request.user.has_perm(f'{opts.app_label}.{codename}')


def has_enable_permission(self, request, obj=None):
    opts = self.opts
    codename = get_permission_codename('enable', opts)
    return request.user.has_perm(f'{opts.app_label}.{codename}')

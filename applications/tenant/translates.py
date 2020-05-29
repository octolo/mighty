from django.utils.translation import gettext_lazy as _

# Role
v_role = _('role')
vp_role = _('roles')

# Tenant
v_tenant = _('tenant')
vp_tenant = _('tenants')

# Invitation
v_invitation = _('invitation')
vp_invitation = _('invitations')

STATE = (
    (0, _('pending')),
    (1, _('accepted')),
    (2, _('cancelled')),
    (3, _('refused')),
)
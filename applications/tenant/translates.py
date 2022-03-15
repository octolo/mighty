from django.utils.translation import gettext_lazy as _

# Role
v_role = _('role')
vp_role = _('roles')

# Tenant
v_tenant = _('tenant')
vp_tenant = _('tenants')

perm_chat_tenantusers = _('Can chat with tenant users')

# Invitation
v_invitation = _('invitation')
vp_invitation = _('invitations')

v_setting = _("tenant configuration")
vp_setting = _("tenants configurations")

STATE = (
    (0, _('pending')),
    (1, _('accepted')),
    (2, _('cancelled')),
    (3, _('refused')),
)

MY = "MY"
ALL = "ALL"
NO = "NO"
SYNC = (
    (MY, _('my direction')),
    (ALL, _('all directions')),
    (NO, _('no direction')),
)
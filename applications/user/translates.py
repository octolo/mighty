from django.utils.translation import gettext_lazy as _

from mighty.apps import MightyConfig as conf

v_user = _('user')
vp_user = _('users')

METHOD_CREATESU = _('Manage.py createsuperuser')
METHOD_BACKEND = _('Backend (/admin)')
METHOD_FRONTEND = _('Workflow allowed by your website')
METHOD_IMPORT = _('By import')

STATUS_PENDING = _('pending')
STATUS_REFUSED = _('refused')
STATUS_ACCEPTED = _('accepted')
STATUS_EXPIRED = _('expired')

GENDER_MAN = _('Homme')
GENDER_WOMAN = _('Femme')
GENDER_COMPANY = _('Company')
GENDER_ENTITY = _('Entity')
GENDER_UNDIVIDED = _('Undivided')

gender_desc = _('Gender of user')
gender = _('Gender')
username = _('Username')
email = _('Email')
phone = _('Phone')
method = _('Creation method')
gender = _('Genre')
profil = _('Profil')
cgu = _(
    "J'accepte les <a href=\"%s\" target=\"blank_\">CGU</a> et la <a href=\"%s\" target=\"blank_\">Politique de Confidentialité</a>" % (
        conf.cgu_path, conf.politic_path
    ))


error_phone_already = _('user with this Phone already exists.')
error_email_already = _('user with this Email already exists.')

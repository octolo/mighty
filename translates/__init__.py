from django.utils.translation import gettext_lazy as _

# Base model
date_create = _('Creation date')
date_update = _('Update date')
create_by = _('Created by')
update_by = _('Updated by')
is_disable = _('Is disable')
alerts = _('Alerts')
errors = _('Errors')

ADD = _('Add')
DETAIL = _('Detail')
LIST = _('List')
CHANGE = _('Change')
DELETE = _('Delete')
DISABLE = _('Disable')
ENABLE = _('Enable')
EXPORT = _('Export')
IMPORT = _('Import')
ANTICIPATE = _('Anticipate')
SOURCE = _('Source')
FILTERLVL0 = _('Filter lvl0 (Keys/Params)')
FILTERLVL1 = _('Filter lvl1 (filters request)')
FILTERLVL2 = _('Filter lvl2 (url expression)')

SITE = _('Site')
DOCUMENT = _('Document')
OTHER = _('other')
NONE = _('none')
YES = _('yes')
NO = _('no')

# Available in views
home = _('home')
login = _('login')
logout = _('logout')
admin = _('Admin')
admin_view = _('Admin view')
nc = _('not disclosed')
next = _('next')
previous = _('previous')

# Descriptions
since = _('since')
until = _('until')
login = _('login')
are_you_sure = _('Are you sure?')
are_you_sure_disable = _('Are you sure you want to disable "%s"?')
are_you_sure_enable = _('Are you sure you want to enable "%s"?')
are_you_sure_delete = _('Are you sure you want to delete "%s"?')
cannot_disable = _('Cannot disable %(name)s')
disable_success = _('Successfully disabled %(count)d %(items)s.')
disable_selected = _('Disable selected %(verbose_name_plural)s')
disable_ok = _('The %(name)s "%(obj)s" was disabled successfully.')
cannot_enable = _('Cannot enable %(name)s')
enable_success = _('Successfully enabled %(count)d %(items)s.')
enable_selected = _('Enable selected %(verbose_name_plural)s')
enable_ok = _('The %(name)s "%(obj)s" was enabled successfully.')
more = _('More')
tasks = _('Tasks')
informations = _('Informations')
alerts_and_errors = _('Alerts and errors')
source = _('Source')
is_in_alert = _('is in alert')
is_in_error = _('is in error')
supervision = _('supervision')
can = _('test')
search = _('search')

# Anticipate model
v_timeline = _('timeline')
vp_timeline = _('timeline')

timeline_desc = _('timeline a change')
model_id = _('associated model')
field = _('field')
value = _('value')
replace = _('replaced by')
fmodel = _('field type')
date_begin = _('begin')
date_end = _('end')

# Source model
v_source = _('source')
vp_source = _('sources')

TYPE_WEBSITE = _('web site')
TYPE_DOCUMENT = _('document')
TYPE_FILE = _('file')
TYPE_IMAGE = _('image')
TYPE_FLUX = _('flux')
TYPE_EVENT = _('event')
TYPE_OTHER = _('other')

no_errors = _('no errors')
error_already_exist = _('already exist')

# export auto
reporting_frequency = _("Fréquence de l'export")
reporting_task_date = _('Date du dernier export')
reporting_email = _("Email de l'export")

FREQUENCY_DAILY = 'DAILY'
FREQUENCY_WEEKLY = 'WEEKLY'
FREQUENCY_MONTHLY = 'MONTHLY'

FREQUENCY_DAILY_TR = _('Quotidien')
FREQUENCY_WEEKLY_TR = _('Hebdomadaire')
FREQUENCY_MONTHLY_TR = _('Mensuel')

FREQUENCY_EXPORT = (
    (FREQUENCY_DAILY, FREQUENCY_DAILY_TR),
    (FREQUENCY_WEEKLY, FREQUENCY_WEEKLY_TR),
    (FREQUENCY_MONTHLY, FREQUENCY_MONTHLY_TR),
)

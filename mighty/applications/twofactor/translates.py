from django.utils.translation import gettext_lazy as _

v_twofactor = _('two factor')
vp_twofactor = _('two factors')

MODE_EMAIL = _('email')
MODE_SMS = _('sms')
STATUS_PREPARE = _('prepare')
STATUS_SENT = _('sent')
STATUS_RECEIVED = _('received')
STATUS_ERROR = _('error')

search = _("""phone number, email or username""")
invalid_search = _("please enter a correct email, phone or username. Note that both fields may be case-sensitive.")
invalid_login = _("please enter a correct %s and password. Note that both fields may be case-sensitive.")
inactive = _("this account is inactive.")
cant_send = _("unable to send message")
method_not_allowed = _("This authentication method is not allowed")

tpl_subject = _("%s - Connection code")
tpl_html = _("here is your personal verification code to connect to the site %s: %s")
tpl_txt = _("here is your personal verification code to connect to the site %s: %s")


help_login = _("Don't have an account? Register")
help_register = _("I already have an account")
help_basic = _("I forget my password")
help_sms = _("I did not get the sms")
help_email = _("I did not get the mail")


howto_email_code = _("enter the code received by Email")
howto_sms_code = _("enter the code received by SMS")
howto_basic_code = _("enter your password")
howto_logout = _("You are disconnected")

send_method = _("method authentication")
send_basic = _("basic authentication")
submit_code = _("sign in")
submit_register = _('sign up')

method_email = _("Email")
method_sms = _("SMS")
method_basic = _("password")

message_email = _("An authenticate code has been sent to the email address %s")
message_sms = _("An authenticate code has been sent to the phone number %s")

register = _('registration')
login = _("sign in")
logout = _("see you soon")
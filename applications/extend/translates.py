from django.utils.translation import gettext_lazy as _

v_key = _('Key')
vp_key = _('keys')

key_type = _('key type')

BIGINTEGER = _('It is a 64-bit integer, much like an IntegerField except that it is guaranteed to fit numbers from -9223372036854775808 to 9223372036854775807.')
BINARY = _('A field to store raw binary data.')
BOOLEAN = _('A true/false field.')
CHAR = _('It is a date, represented in Python by a datetime.date instance.')
DATE = _('A date, represented in Python by a datetime.date instance')
DECIMAL = _('It is a fixed-precision decimal number, represented in Python by a Decimal instance.')
DURATION = _('A field for storing periods of time.')
EMAIL = _('It is a CharField that checks that the value is a valid email address.')
FILE = _('It is a file-upload field.')
FLOAT = _('It is a floating-point number represented in Python by a float instance.')
IMAGE = _('It inherits all attributes and methods from FileField, but also validates that the uploaded object is a valid image.')
INTEGER = _('It is an integer field. Values from -2147483648 to 2147483647 are safe in all databases supported by Django.')
SMALLINTEGER = _('It is like an IntegerField, but only allows values under a certain (database-dependent) point.')
TEXT = _('A large text field. The default form widget for this field is a Textarea.')
TIME = _('A time, represented in Python by a datetime.time instance.')
URL = _('A CharField for a URL, validated by URLValidator.')

v_value = _('Value')
vp_value = _('Values')

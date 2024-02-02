default_app_config = 'mighty.applications.user.apps.UserConfig'

from django.contrib.auth import get_user_model
from mighty.applications.user.apps import UserConfig as conf
import uuid

#FIXME: Need unique method to create user

# def username_generator(base_username):
#     UserModel = get_user_model()
#     prefix = "".join([l for l in base_username if l.isalpha()])
#     prefix = prefix[:3] if len(prefix) >= 3 else prefix
#     exist = True
#     while exist:
#         username = '%s%s' % ('%s-' % prefix if prefix else '', str(uuid.uuid4())[:8])
#         username = username.lower()
#         try:
#             UserModel.objects.get(username=username)
#         except UserModel.DoesNotExist:
#             exist = False
#     return username

def get_form_fields(fields='*'):
    if fields == '*':
        return (conf.Field.username,) + conf.Field.required + conf.Field.optional
    else:
        return getattr(conf.Field, fields)

# DEV
def username_generator_v2(first_name=None, last_name=None, email=None):
    """
    Generate a unique username based on the first name, surname, and/or email address.

    :param first_name: The first name of the user (optional).
    :param surname: The surname of the user (optional).
    :param email: The email address of the user (optional).
    :return: A unique username string.
    """

    # Check if first name and surname are provided
    if first_name and last_name:
        # Use the first name and surname to generate the prefix
        prefix = f"{last_name[0].lower()}{first_name[:2].lower()}"
    elif email:
        # Validate the email
        if '@' not in email:
            raise ValueError("A valid email must be provided")

        # Split the email into local part and domain
        local_part, domain = email.split('@')

        # Use a combination of parts of the local part and domain for the prefix
        prefix = f"{local_part[:3].lower()}-{domain.split('.')[0][:3].lower()}"
    else:
        raise ValueError("Insufficient information: provide either first name and surname, or email")

    # Get the user model
    UserModel = get_user_model()

    # Generate a unique username
    while True:
        # Create a candidate username by combining the prefix and a substring of a UUID
        username = f"{prefix}-{str(uuid.uuid4())[:8]}"

        # Check if the username already exists in the database
        if not UserModel.objects.filter(username=username).exists():
            return username  # Return the username if it's unique

    # Note: The loop will continue until a unique username is found

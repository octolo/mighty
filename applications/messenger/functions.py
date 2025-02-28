from django.contrib.auth import get_user_model

from mighty.applications.messenger.apps import MessengerConfig as conf

User = get_user_model()


def explain_room(room_name):
    room = room_name.split(conf.delimiter)
    obj_by = room[0]
    obj_for = room[1]
    try:
        obj_by = int(obj_by)
        User.objects.get(id=obj_by)
    except ValueError:
        User.objects.get(uid=obj_by)
    except User.DoesNotExist:
        pass

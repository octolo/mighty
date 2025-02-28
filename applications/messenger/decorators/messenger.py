from django.conf import settings
from django.contrib.contenttypes.fields import (
    GenericForeignKey,
    GenericRelation,
)
from django.contrib.contenttypes.models import ContentType
from django.db.models import (
    SET_NULL,
    CharField,
    ForeignKey,
    PositiveIntegerField,
)

from mighty.applications.messenger.models import MessengerModel


def HeritToMessenger(**kwargs):
    def decorator(obj):
        class NewClass(obj, MessengerModel):
            backend = CharField(
                max_length=255,
                blank=kwargs.get('backend_blank', True),
                null=kwargs.get('backend_null', True),
                editable=False,
            )
            content_type = ForeignKey(
                ContentType,
                on_delete=kwargs.get('on_delete', SET_NULL),
                blank=kwargs.get('blank', True),
                null=kwargs.get('null', True),
                related_name=kwargs.get(
                    'related_name', 'content_type_to_messenger'
                ),
            )
            object_id = PositiveIntegerField(
                blank=kwargs.get('blank', True),
                null=kwargs.get('null', True),
            )
            content_object = GenericForeignKey('content_type', 'object_id')

            class Meta:
                abstract = True

            @property
            def object_for_this_type(self):
                return self.content_type.get_object_for_this_type(
                    id=self.object_id
                )

            @property
            def admin_url(self):
                return self.object_for_this_type.admin_change_url

            @property
            def admin_url_html(self):
                obj = self.object_for_this_type
                return self.get_url_html(obj.admin_change_url, str(obj))

        NewClass.__name__ = obj.__name__
        return NewClass

    return decorator


def AccessToMissive(**kwargs):
    def decorator(obj):
        if 'mighty.applications.messenger' in settings.INSTALLED_APPS:
            obj.add_to_class(
                'missives',
                GenericRelation(kwargs.get('foreignkey', 'mighty.Missive')),
            )
            obj.add_to_class(
                'messenger_missives',
                GenericRelation(kwargs.get('foreignkey', 'mighty.Missive')),
            )
        return obj

    return decorator

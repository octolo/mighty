from django.db.models import PositiveIntegerField, ForeignKey, CharField, SET_NULL
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from mighty.applications.messenger.models import MessengerModel
from django.conf import settings

def HeritToMessenger(**kwargs):
    def decorator(obj):
        class NewClass(obj, MessengerModel):
            backend = CharField(
                max_length=255,
                blank=kwargs.get("backend_blank", True),
                null=kwargs.get("backend_null", True),
                editable=False
            )
            content_type = ForeignKey(ContentType,
                on_delete=kwargs.get("on_delete", SET_NULL),
                blank=kwargs.get("blank", True),
                null=kwargs.get("null", True),
                related_name=kwargs.get("related_name", "content_type_to_messenger"),
            )
            object_id = PositiveIntegerField(
                blank=kwargs.get("blank", True),
                null=kwargs.get("null", True),
            )
            content_object = GenericForeignKey('content_type', 'object_id')

            class Meta:
                abstract = True

            @property
            def object_for_this_type(self):
                return self.content_type.get_object_for_this_type(id=self.object_id)

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
            obj.add_to_class("missives", GenericRelation(kwargs.get("foreignkey", "mighty.Missive")))
            obj.add_to_class("messenger_missives", GenericRelation(kwargs.get("foreignkey", "mighty.Missive")))
        return obj
    return decorator

def AdminMissivesView(**kwargs):
    def decorator(obj):
        class NewClass(obj):

            def missives_view(self, request, object_id, form_url=None, extra_context=None):
                from django.core.paginator import Paginator
                from django.contrib.admin.options import TO_FIELD_VAR
                from django.contrib.admin.utils import unquote
                to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
                obj = self.get_object(request, unquote(object_id), to_field)
                paginator = Paginator(obj.messenger_missives.all(), 25)
                page = request.GET.get('page', 1)
                extra_context = { "missives": paginator.get_page(page), }
                return self.admincustom_view(request, object_id, extra_context,
                    urlname=self.get_admin_urlname("missives"),
                    template="admin/missives.html",
                )

            def get_urls(self):
                from django.urls import path, include
                urls = super().get_urls()
                my_urls = [
                    path("<path:object_id>/missives/",
                        self.wrap(self.missives_view, object_tools={"name": "Missives", "url": "missives"}),
                        name=self.get_admin_urlname("missives"),
                    ),
                ]
                return my_urls + urls

        NewClass.__name__ = obj.__name__
        return NewClass
    return decorator

from django.contrib.contenttypes.fields import GenericRelation

def AccessToRegisterTask(**kwargs):
    def decorator(obj):
        from django.contrib.contenttypes.models import ContentType
        from mighty.models import RegisterTaskSubscription

        class NewClass(obj):
            @property
            def registered_tasks(self):
                ct = ContentType.objects.get_for_model(self)
                return RegisterTaskSubscription.objects.filter(
                    object_id_subscriber=self.pk,
                    content_type_subscriber=ct,
                )

            class Meta(obj.Meta):
                abstract = obj._meta.abstract

        NewClass.__name__ = obj.__name__
        return NewClass
    return decorator

def AdminRegisteredTasksView(**kwargs):
    def decorator(obj):
        class NewClass(obj):

            def registertask_view(self, request, object_id, form_url=None, extra_context=None):
                from django.core.paginator import Paginator
                from django.contrib.admin.options import TO_FIELD_VAR
                from django.contrib.admin.utils import unquote
                to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
                obj = self.get_object(request, unquote(object_id), to_field)
                paginator = Paginator(obj.registered_tasks.all(), 25)
                page = request.GET.get('page', 1)
                extra_context = { "registered_tasks": paginator.get_page(page), }
                return self.admincustom_view(request, object_id, extra_context,
                    urlname=self.get_admin_urlname("registered_tasks"),
                    template="admin/registered_tasks.html",
                    title="Registered Tasks list"
                )

            def get_urls(self):
                from django.urls import path, include
                urls = super().get_urls()
                my_urls = [
                    path("<path:object_id>/registered_tasks/",
                        self.wrap(self.registertask_view, object_tools={"name": "Registered Tasks", "url": "registered_tasks"}),
                        name=self.get_admin_urlname("registered_tasks"),
                    ),
                ]
                return my_urls + urls

        NewClass.__name__ = obj.__name__
        return NewClass
    return decorator

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
            registertask_object_tools = {"name": "Replay", "url": "registertask",}
            registertask_admin_path = "<path:object_id>/registered_tasks/"
            registertask_admin_template = "admin/registered_tasks.html"
            registertask_admin_suffix = "registertask"

            def registertask_view(self, request, object_id=None, form_url=None, extra_context=None):
                from django.core.paginator import Paginator
                paginator = Paginator(obj.registered_tasks.all(), 25)
                page = request.GET.get('page', 1)
                extra_context = { "registered_tasks": paginator.get_page(page), }
                return self.admincustom_view(request, object_id, extra_context,
                    urlname=self.get_admin_urlname(self.registertask_admin_suffix),
                    template=self.registertask_admin_template,
                )

            def get_urls(self):
                from django.urls import path, include
                urls = super().get_urls()
                my_urls = [
                    path(
                        self.registertask_admin_path,
                        self.wrap(self.registertask_view, object_tools=self.registertask_object_tools),
                        name=self.get_admin_urlname(self.registertask_admin_suffix),
                    ),
                ]
                return my_urls + urls

        NewClass.__name__ = obj.__name__
        return NewClass
    return decorator

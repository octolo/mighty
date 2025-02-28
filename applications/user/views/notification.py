from django.conf import settings

if 'mighty.applications.messenger' in settings.INSTALLED_APPS:
    from django.contrib.auth import get_user_model
    from django.contrib.auth.decorators import login_required
    from django.contrib.contenttypes.models import ContentType
    from django.db.models import Q
    from django.http import JsonResponse
    from django.utils.decorators import method_decorator

    from mighty.applications.messenger import choices
    from mighty.applications.user.apps import UserConfig
    from mighty.functions import get_model
    from mighty.models import Missive
    from mighty.views import DetailView, ListView

    UserModel = get_user_model()

    class NotificationBaseView:
        model = Missive
        queryset = Missive.objects.all()

        def get_Qrelation(self, model, relation):
            model = get_model(*model.split('.'))
            return {
                'content_type': ContentType.objects.get_for_model(model()),
                'object_id__in': model.objects.filter(**{relation: self.request.user}).values_list('id', flat=True),
            }

        @property
        def Qfilter(self):
            user_content_type = ContentType.objects.get_for_model(UserModel())
            baseQ = Q(content_type=user_content_type, object_id=self.request.user.id)
            for m, r in UserConfig.notification_optional_relation.items():
                baseQ |= Q(**self.get_Qrelation(m, r))
            return baseQ

        def get_queryset(self, queryset=None):
            return self.queryset.filter(self.Qfilter)

        def get_object_serialized(self, notif):
            return {
                'uid': str(notif.uid),
                'subject': str(notif.subject),
                'date_create': str(notif.date_create),
                'target': str(notif.target),
                'content': str(notif.content),
                'status': str(notif.status),
            }

        def get_stats(self):
            return {'unread': self.get_queryset().exclude(status=choices.STATUS_OPEN).count()}

        def get_results(self):
            return [self.get_object_serialized(notif) for notif in self.get_queryset()]

        def get_serialized_data(self):
            return {'stats': self.get_stats(), 'results': self.get_results()}

    @method_decorator(login_required, name='dispatch')
    class NotificationListView(NotificationBaseView, ListView):
        queryset = Missive.objects.all()

        def get_context_data(self, **kwargs):
            return self.get_serialized_data()

        def render_to_response(self, context, **response_kwargs):
            return JsonResponse(context, **response_kwargs)

    @method_decorator(login_required, name='dispatch')
    class NotificationDetailView(NotificationBaseView, DetailView):
        queryset = Missive.objects.all()
        slug_field = 'uid'
        slug_url_kwarg = 'uid'

        def get_context_data(self, **kwargs):
            return self.get_object_serialized(self.get_object())

        def render_to_response(self, context, **response_kwargs):
            return JsonResponse(context, **response_kwargs)


if 'rest_framework' in settings.INSTALLED_APPS:
    from rest_framework.generics import ListAPIView, RetrieveAPIView
    from rest_framework.response import Response

    class NotificationListView(NotificationBaseView, ListAPIView):
        queryset = Missive.objects.all()

        def get_context_data(self, **kwargs):
            return self.get_serialized_data()

        def get(self, context, **response_kwargs):
            return Response(self.get_serialized_data())

    class NotificationDetailView(NotificationBaseView, RetrieveAPIView):
        queryset = Missive.objects.all()
        lookup_field = 'uid'

        def get_context_data(self, **kwargs):
            return self.get_serialized_data()

        def get(self, context, **response_kwargs):
            return Response(self.get_object_serialized(self.get_object()))

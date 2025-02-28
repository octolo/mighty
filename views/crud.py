from django.http import HttpResponseRedirect
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from mighty.functions import setting
from mighty.views.foxid import FoxidView
from mighty.views.model import ModelView


# ListView overrided
class ListView(FoxidView, ListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': self.model._meta.verbose_name_plural})
        return context


# CreateView overrided and rename with an empty object
class AddView(ModelView, CreateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': '{} {}'.format(
                self.model.mighty.perm_title['add'],
                self.model._meta.verbose_name,
            )
        })
        return context

    def get_success_url(self):
        return self.object.detail_url


# DetailView overrided
class DetailView(ModelView, DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'title': self.object})
        return context


# ChangeView overrided
class ChangeView(ModelView, UpdateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': '{} {}'.format(
                self.model.mighty.perm_title['change'],
                self.model._meta.verbose_name,
            )
        })
        return context

    def get_success_url(self):
        return self.object.detail_url


# DeleteView overrided
class DeleteView(ModelView, DeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': '{} {}'.format(
                self.object.mighty.perm_title['delete'],
                self.object._meta.verbose_name,
            )
        })
        return context

    def get_success_url(self):
        return self.object.list_url

        # EnableView is like deleteview but set is_disable to false


class EnableView(DeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': '{} {}'.format(
                self.model.mighty.perm_title['enable'],
                context['fake']._meta.verbose_name,
            )
        })
        return context

    def get_success_url(self):
        return self.object.detail_url

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.enable()
        return HttpResponseRedirect(success_url)


# EnableView is like deleteview but set is_disable to true
class DisableView(DeleteView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': '{} {}'.format(
                self.model.mighty.perm_title['disable'],
                self.object._meta.verbose_name,
            )
        })
        return context

    def get_success_url(self):
        return self.object.list_url

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.disable()
        return HttpResponseRedirect(success_url)


if 'rest_framework' in setting('INSTALLED_APPS'):
    from rest_framework.generics import DestroyAPIView
    from rest_framework.response import Response

    # DisableApiView add a view for disable an object (set is_disable to true)
    class DisableApiView(DestroyAPIView):
        def delete(self, request, *args, **kwargs):
            return self.disable(request, *args, **kwargs)

        def disable(self, request, *args, **kwargs):
            instance = self.get_object()
            instance = self.perform_disable(instance)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        def perform_disable(self, instance):
            return instance.disable()

    # EnableApiView add a view for enable an object (set is_disable to false)
    class EnableApiView(DestroyAPIView):
        def delete(self, request, *args, **kwargs):
            return self.enable(request, *args, **kwargs)

        def enable(self, request, *args, **kwargs):
            instance = self.get_object()
            instance = self.perform_enable(instance)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        def perform_enable(self, instance):
            return instance.enable()

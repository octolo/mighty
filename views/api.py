from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework import status

# ListApiView that allow to use a filter_model
class ListAPIView(ListAPIView):
    pass
    # def get_queryset(self):
    #     if self.filter_model is None: return super().get_queryset()
    #     else: return self.filter_model(self.request)

# DisableApiView add a view for disable an object (set is_disable to true)
class DisableApiView(DestroyAPIView):
    def delete(self, request, *args, **kwargs):
        return self.disable(request, *args, **kwargs)

    def disable(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_disable(instance)
        return Response(status=status.HTTP_200_OK)

    def perform_disable(self, instance):
        instance.disable()

# EnableApiView add a view for enable an object (set is_disable to false)
class EnableApiView(DestroyAPIView):
    def delete(self, request, *args, **kwargs):
        return self.enable(request, *args, **kwargs)

    def enable(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_enable(instance)
        return Response(status=status.HTTP_200_OK)

    def perform_enable(self, instance):
        instance.enable()

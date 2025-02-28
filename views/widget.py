from mighty.views.template import TemplateView


# Return an html widget
class Widget(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'id': self.kwargs['id']})
        return context

    def get_template_names(self):
        return 'widgets/%s.html' % self.kwargs['widget']

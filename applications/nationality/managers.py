from django.db.models import Manager, QuerySet

TranslateDict_Select_related = ('translator',)


class TranslateDictManager(Manager.from_queryset(QuerySet)):
    def get_queryset(self):
        return (
            super().get_queryset().select_related(*TranslateDict_Select_related)
        )

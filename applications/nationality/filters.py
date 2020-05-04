from mighty.filters import Filter
from mighty.models.applications.nationality import Nationality
from mighty.applications.nationality.fields import searchs, params

def NationalityFilter(view, request):
    NationalityFilter = Filter(request, Nationality)
    for search in searchs: NationalityFilter.add_param("search", search)
    for search in searchs: NationalityFilter.add_param("searchex", search, mask="iexact")
    for param in params: NationalityFilter.add_param(param, param)
    return NationalityFilter.get()
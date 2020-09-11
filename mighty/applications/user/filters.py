from mighty.filters import Filter
from mighty.models import User
from mighty.applications.user.fields import search, params

def UserFilter(view, request):
    UserFilter = Filter(request, User)
    for search in search: UserFilter.add_param("search", search)
    for search in search: UserFilter.add_param("searchex", search, mask="iexact")
    for param in params: UserFilter.add_param(param, param)
    return UserFilter.get()
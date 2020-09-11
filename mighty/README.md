# H1 Mighty
Mighty is a python library that improves the functionality of the django framework.

# H2 Configuration
How to add mighty to your project.

# H3 edit your settings.py
Add dependencies
```python
INSTALLED_APPS += [
    'phonenumber_field', 
    'django_json_widget',
]
```

Add the library.
```python
INSTALLED_APPS += [
    'mighty', # adds powerful tools that facilitate application development
    'mighty.applications.user', # Improves user with multiple mails and phones
    'mighty.applications.nationality', # Create a nationality object (automatically add nationality to users)
    'mighty.applications.twofactor', # Enable a twofactor method authentication
    'mighty.applications.grapher', # Enable an application to generate svg or canvas graphics
]
```

If you enable the "mighty.applications.user" you need to change your USER_MODEL.
```python
AUTH_USER_MODEL = 'mighty.User'
```

# H3 edit your urls.py
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mighty.urls')),
]
```

# H2 Use Mighty
Mighty can extend the model base and generate all view model via a viewset class.

# H3 Extend Model
You can extend your model base with some class.


# H4 Class base
This class allows you to access the different model management links.

```python
from mighty.models.base import Base

class Model(Base):
    field...

Model.admin_list_url # return admin URL list
Model.admin_add_url # return admin URL add
Model.admin_change_url # return admin URL change
Model.add_url # return URL add
Model.list_url # return URL list
Model.detail_url # return URL detail
Model.change_url # return URL change
Model.delete_url # return URL delete
Model.add_url_html # return URL add HTML link
Model.list_url_html # return URL list HTML link
Model.detail_url_html # return URL detail HTML link
Model.change_url_html # return URL change HTML link
Model.delete_url_html # return URL delete HTML link
```

# H4 Class uid
This class add an UID field to your model.
She also override all urls properties with this field as an ID mask.

```python
from mighty.models.uid import Uid
class Model(Uid):
    field...
```

# H4 Class Alert
This class add a Alert field to your model.

```python
from mighty.models.alert import Alert
```
# H4 Class Code
This class add a Code field to your model
You need to configure the code_fields array that contains all field to use for generate a code.

```python
from mighty.models.code import Code

class Model(Code):
    code_fields = ['field1', 'field2']
```

# H4 Class Disable
This class add a Disable field to your model.

```python
from mighty.models.disable import Disable

class Model(Disable):
    fields...

Model.disable_url # return URL to disable
Model.enable_url # return URL to enable
```
# H4 Class Display
This class add a Display field to your model.

```python
from mighty.models.display import Display

class Model(Display):
    fields...
```
# H4 Class File
This class add a file, filename and filemimetype fields to your model.

```python
from mighty.models.file import File

class Model(File):
    fields...
```
# H4 Class Image
This class add a Image field to your model.

```python
from mighty.models.image import Image

class Model(Image):
    fields...
```
# H4 Class Keyword
This class add a Keyword field to your model.
You need to configure the keyword_fields array that contains all field to use for generate an array contain keywords.

```python
from mighty.models.keyword import Keyword

class Model(Keyword):
    fields...
```
# H4 Class Search
This class add a Search field to your model
You need to configure the search_fields array that contains all field to use for generate an textfield contain searchable fields.

```python
from mighty.models.search import Search

class Model(Search):
    fields...
```
# H4 Class source
This class add a source field to your model.

```python
from mighty.models.source import Source

class Model(Source):
    fields...
```

# H3 Viewset
You can generate all of your views (detail, change, create, update, enable, disable, delete) with a viewset to automize the processus.

# H4 Model Viewset

```python
from mighty.views.viewsets import ModelViewSet

class ModelViewSet(ModelViewSet):
    model = Model
    slug = '<uuid:uid>' # Slug mask
    slug_field = "uid" # Slug field
    slug_url_kwarg = "uid" # Slug url arg
    list_is_ajax = True # enable ajax model with ApiViewSet URL, get_queryset_ return None
    filter_model = ModelFilter

    def __init__(self):
        super().__init__()
        self.add_view('newview', ModelNewView, 'newview/') # add a view
        self.add_view('newview_with_arg', ModelNewViewDetail, 'newview/%s/' % self.slug) # add a view with an url arg
```

# H4 Model ApiViewSet

```python
from mighty.views.viewsets import ApiModelViewSet

class UserApiViewSet(ApiModelViewSet):
    model = Model
    slug = '<uuid:uid>'
    slug_field = "uid"
    slug_url_kwarg = "uid"
    lookup_field = "uid"
    serializer_class = serializers.ModelSerializer
    filter_model = ModelFilter
```

# H3 Filter

```python
from mighty.filters import Filter

def ModelFilter(view, request):
    ModelFilter = Filter(request, Resolution)
    ModelFilter.add_param("GET/POST key", "mask__queryset")
    return ModelFilter.get()
```
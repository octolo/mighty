from mighty import fields
searchs = ('country', 'alpha2', 'alpha3', 'numeric')
params = ('id', 'country', 'alpha2', 'alpha3', 'numeric')

serializer = fields.detail_url + fields.image_url + (
    'country',
    'alpha2',
    'alpha3',
    'numeric',
)
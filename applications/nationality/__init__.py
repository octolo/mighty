default_app_config = 'mighty.applications.nationality.apps.NationalityConfig'

import json
def conf_prefix_numbering():
    from mighty.models import Nationality
    return [
        {"country": nat.country, "alpha2": nat.alpha2, "numbering": nat.numbering, "flag": nat.image_url}
        for nat in Nationality.objects.filter(numbering__isnull=False)]
    
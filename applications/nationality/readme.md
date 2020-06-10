# Nationality
Add a model in base with fields:

- country, name country
- alpha2, code alpha 2
- alpha3, code alpha 3
- numeric, numeric code country
- numbering, calling code
- image, flag png

## Command
You can fill database by default with this command:

    ./manage.py LoadNationalitiesInDatabase --csv mighty/applications/nationality/countries.csv

## Usage
You can use this model by import

    from mighty.models import Nationality
    obj = Nationality.objects.first()

	# return tag <img src="{{ static_url }}" alt="{{ __str__ }}">
    obj.image_hml

	# Join model
	models.ForeignKey(Nationality, on_delete=models.CASCADE)
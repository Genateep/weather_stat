from django.db import migrations

CITIES = [
        'Moscow',
        'Saint Petersburg',
        'Novosibirsk',
        'Ekaterinburg',
        'Kazan',
        'Nizhniy Novgorod',
        'Chelyabinsk',
        'Samara',
        'Vladivostok',
        'Murmansk',
        'Helsinki',
        'Minsk',
        'Berlin',
        'Paris',
        'London'
    ]


class Migration(migrations.Migration):

    def db_recording(apps, schema_editor):
        cityList = apps.get_model("statApp", "CityList")

        for city in CITIES:
            c = cityList(city=city)
            c.save()

    dependencies = [
        ("statApp", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(db_recording),
    ]

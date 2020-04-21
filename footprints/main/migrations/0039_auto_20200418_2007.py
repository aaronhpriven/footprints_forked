# Generated by Django 2.2.12 on 2020-04-19 00:07

from django.db import migrations


def display_title(city, country):
    parts = []
    if city:
        parts.append(city)
    if country:
        parts.append(country)

    return ', '.join(parts)


def migrate_city_country(apps, schema_editor):
    Place = apps.get_model('main', 'Place')
    for place in Place.objects.all():
        title = display_title(place.city, place.country)
        place.alternate_name = title
        place.canonical_name = title
        place.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0038_auto_20200418_2003'),
    ]

    operations = [
        migrations.RunPython(migrate_city_country),
    ]

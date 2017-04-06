import re

from celery_haystack.indexes import CelerySearchIndex
from haystack.constants import Indexable
from haystack.fields import CharField, NgramField, DateTimeField, IntegerField
from unidecode import unidecode

from footprints.main.models import WrittenWork, Footprint, Person, Place, \
    Imprint


def format_sort_by(sort_term, remove_articles=False):
    ''' processes text for sorting field:
        * converts non-ASCII characters to ASCII equivalents
        * converts to lowercase
        * (optional) remove leading a/the
        * removes outside spaces
    '''
    sort_term = unidecode(sort_term).lower().strip()
    if remove_articles:
        sort_term = re.sub(r'^(a\s+|the\s+)', '', sort_term)
    return sort_term


class WrittenWorkIndex(CelerySearchIndex, Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = NgramField(document=True, use_template=True)
    title = NgramField(model_attr='title', null=True)
    sort_by = CharField()

    def get_model(self):
        return WrittenWork

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_sort_by(self, obj):
        return format_sort_by(obj.__unicode__(), remove_articles=True)


class ImprintIndex(CelerySearchIndex, Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = NgramField(document=True, use_template=True)
    title = NgramField(model_attr='title', null=True)

    def get_model(self):
        return Imprint

    def prepare_object_type(self, obj):
        return type(obj).__name__


class FootprintIndex(CelerySearchIndex, Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = NgramField(document=True, use_template=True)
    title = NgramField(model_attr='title')
    sort_by = CharField()
    footprint_start_date = DateTimeField()
    footprint_end_date = DateTimeField()

    # custom sort fields
    added = DateTimeField(model_attr='created_at')
    complete = IntegerField(model_attr='percent_complete')
    ftitle = CharField()
    fdate = DateTimeField()
    flocation = CharField()
    owners = CharField()
    wtitle = CharField()

    def get_model(self):
        return Footprint

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_sort_by(self, obj):
        return format_sort_by(obj.title, remove_articles=True)

    def prepare_ftitle(self, obj):
        try:
            return format_sort_by(obj.title, remove_articles=True)
        except AttributeError:
            return ''

    def prepare_flocation(self, obj):
        if obj.place:
            return obj.place.__unicode__()

        return ''

    def prepare_fdate(self, obj):
        return obj.sort_date()

    def prepare_footprint_end_date(self, obj):
        return obj.end_date()

    def prepare_footprint_start_date(self, obj):
        return obj.start_date()

    def prepare_wtitle(self, obj):
        try:
            return format_sort_by(obj.book_copy.imprint.work.title,
                                  remove_articles=True)
        except AttributeError:
            return ''

    def prepare_owners(self, obj):
        a = [o.display_name() for o in obj.owners()]
        return format_sort_by(', '.join(a), remove_articles=True)


class PersonIndex(CelerySearchIndex, Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = NgramField(document=True, use_template=True)
    name = NgramField(model_attr='name')
    sort_by = CharField()

    def get_model(self):
        return Person

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_sort_by(self, obj):
        return format_sort_by(obj.name, remove_articles=True)


class PlaceIndex(CelerySearchIndex, Indexable):
    object_id = CharField(model_attr='id')
    object_type = CharField()
    text = NgramField(document=True, use_template=True)
    sort_by = CharField()

    def get_model(self):
        return Place

    def prepare_object_type(self, obj):
        return type(obj).__name__

    def prepare_sort_by(self, obj):
        return format_sort_by(obj.__unicode__(), remove_articles=True)

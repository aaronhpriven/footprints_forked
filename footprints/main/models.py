from django.db import models
from geoposition.fields import GeopositionField
from audit_log.models.fields import LastUserField, CreatingUserField


CONTINENTS = (
    ('AF', 'Africa'),
    ('AS', 'Asia'),
    ('EU', 'Europe'),
    ('NA', 'North America'),
    ('SA', 'South America'),
    ('OC', 'Oceania'),
    ('AN', 'Antarctica'))


IDENTIFIER_TYPES = (
    ('LOC', 'Library of Congress'),
    ('BHB', 'Bibliography of the Hebrew Book'),
    ('WLD', 'WorldCat (OCLC)'),
    ('VIAF', 'VIAF Identifier'),
    ('GETT', 'The Getty Thesaurus of Geographic Names')
)

HIDDEN_FIELDS = ['id']


def get_model_fields(the_model):
    return [field.name for field in the_model._meta.fields
            if field.name not in HIDDEN_FIELDS]


class ExtendedDateFormat(models.Model):
    edtf_format = models.CharField(max_length=256)

    class Meta:
        verbose_name = 'Extended Date Format'

    def __unicode__(self):
        return self.edtf_format


class RoleQuerySet(models.query.QuerySet):
    def get_author_role(self):
        role, created = self.get_or_create(name='Author')
        return role


class RoleManager(models.Manager):
    def __init__(self, fields=None, *args, **kwargs):
        super(RoleManager, self).__init__(*args, **kwargs)
        self._fields = fields

    def get_query_set(self):
        return RoleQuerySet(self.model, self._fields)

    def get_author_role(self):
        return self.get_query_set().get_author_role()


class Role(models.Model):
    objects = RoleManager()

    name = models.CharField(max_length=256, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Role'

    def __unicode__(self):
        return self.name


class Name(models.Model):
    name = models.TextField()
    sort_by = models.TextField()

    created_by = CreatingUserField(related_name="name_created_by")
    last_modified_by = LastUserField(related_name="name_last_modified_by")

    class Meta:
        ordering = ['sort_by', 'name']
        verbose_name = 'Name'

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.sort_by is None or len(self.sort_by) < 1:
            self.sort_by = self.name
        super(Name, self).save(*args, **kwargs)


class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Language'

    def __unicode__(self):
        return self.name


class DigitalFormat(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Digital Format"

    def __unicode__(self):
        return self.name


class DigitalObject(models.Model):
    name = models.CharField(max_length=500)
    digital_format = models.ForeignKey(DigitalFormat)
    file = models.FileField(upload_to="digitalobjects/%Y/%m/%d/")

    source_url = models.URLField(null=True)
    notes = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name="digitalobject_created_by")
    last_modified_by = LastUserField(
        related_name="digitalobject_last_modified_by")

    class Meta:
        verbose_name = "Digital Object"
        ordering = ['name']

    def __unicode__(self):
        return self.name


class StandardizedIdentification(models.Model):
    identifier = models.CharField(max_length=512)
    identifier_type = models.CharField(max_length=5, choices=IDENTIFIER_TYPES)
    identifier_text = models.TextField(null=True)
    permalink = models.URLField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(
        related_name='standardizedidentification_created_by')
    last_modified_by = LastUserField(
        related_name='standardizedidentification_last_modified_by')

    class Meta:
        verbose_name = "Standardized Identification"

    def __unicode__(self):
        return self.identifier

    def authority(self):
        return dict(IDENTIFIER_TYPES)[self.identifier_type]


class Person(models.Model):
    name = models.OneToOneField(Name, related_name="person_name")

    birth_date = models.OneToOneField(ExtendedDateFormat,
                                      null=True,
                                      related_name="birth_date")
    death_date = models.OneToOneField(ExtendedDateFormat,
                                      null=True,
                                      related_name="death_date")

    standardized_identifier = models.ForeignKey(StandardizedIdentification,
                                                null=True)
    digital_object = models.ManyToManyField(
        DigitalObject, null=True)

    notes = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='person_created_by')
    last_modified_by = LastUserField(related_name='person_last_modified_by')

    class Meta:
        verbose_name = "Person"
        ordering = ['name']

    def __unicode__(self):
        return "%s" % self.name.__unicode__()

    def percent_complete(self):
        required = 6.0
        complete = 1  # name is required

        if self.birth_date is not None:
            complete += 1
        if self.death_date is not None:
            complete += 1
        if self.standardized_identifier is not None:
            complete += 1
        if self.digital_object.count() > 0:
            complete += 1
        if self.notes is not None and len(self.notes) > 0:
            complete += 1
        return int(complete/required * 100)


class Actor(models.Model):
    person = models.ForeignKey(Person)
    role = models.ForeignKey(Role)
    actor_name = models.OneToOneField(Name,
                                      related_name="actor_name",
                                      null=True)

    notes = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='actor_created_by')
    last_modified_by = LastUserField(
        related_name='actor_last_modified_by')

    def display_name(self):
        if self.actor_name:
            return self.actor_name.__unicode__()
        else:
            return self.person.name.__unicode__()

    def __unicode__(self):
        return "%s (%s)" % (self.display_name(), self.role)


class Place(models.Model):
    continent = models.CharField(max_length=2, choices=CONTINENTS)
    region = models.CharField(max_length=256, null=True)
    country = models.CharField(max_length=256, null=True)
    city = models.CharField(max_length=256, null=True)

    position = GeopositionField(null=True)

    digital_object = models.ManyToManyField(
        DigitalObject, null=True)

    notes = models.TextField(null=True)

    standardized_identification = models.ForeignKey(StandardizedIdentification,
                                                    null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='place_created_by')
    last_modified_by = LastUserField(related_name='place_last_modified_by')

    class Meta:
        ordering = ['continent', 'region', 'country', 'city']
        verbose_name = "Place"

    def __unicode__(self):
        parts = []
        if self.city:
            parts.append(self.city)
        if self.country:
            parts.append(self.country)
        if self.region:
            parts.append(self.region)
        parts.append(dict(CONTINENTS)[self.continent])

        return ', '.join(parts)


class Collection(models.Model):
    name = models.CharField(max_length=512, unique=True)
    actor = models.ManyToManyField(Actor, null=True)

    notes = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='collection_created_by')
    last_modified_by = LastUserField(
        related_name='collection_last_modified_by')

    class Meta:
        ordering = ['name']
        verbose_name = "Collection"

    def __unicode__(self):
        return self.name


class WrittenWork(models.Model):
    title = models.TextField()
    actor = models.ManyToManyField(
        Actor, null=True,
        help_text="The author or creator of the work. ")
    notes = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='writtenwork_created_by')
    last_modified_by = LastUserField(
        related_name='writtenwork_last_modified_by')

    class Meta:
        ordering = ['title']
        verbose_name = "Written Work"

    def __unicode__(self):
        return self.title

    def percent_complete(self):
        required = 3.0
        complete = 1  # title is required

        if self.actor.count() > 0:
            complete += 1
        if self.notes is not None and len(self.notes) > 0:
            complete += 1
        return int(complete/required * 100)


class Imprint(models.Model):
    work = models.ForeignKey(WrittenWork, null=True)

    title = models.TextField(null=True)
    language = models.ForeignKey(Language, null=True)
    date_of_publication = models.OneToOneField(ExtendedDateFormat, null=True)
    place = models.ForeignKey(Place, null=True)

    actor = models.ManyToManyField(Actor, null=True)

    standardized_identifier = models.ManyToManyField(
        StandardizedIdentification, null=True)

    digital_object = models.ManyToManyField(
        DigitalObject, null=True)

    notes = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='imprint_created_by')
    last_modified_by = LastUserField(related_name='imprint_last_modified_by')

    class Meta:
        ordering = ['work']
        verbose_name = "Imprint"

    def __unicode__(self):
        label = 'Imprint'
        if self.title:
            label = self.title
        elif self.work:
            label = self.work.title

        if self.date_of_publication:
            label = "%s (%s)" % (label, self.date_of_publication)
        return label


class BookCopy(models.Model):
    imprint = models.ForeignKey(Imprint)

    digital_object = models.ManyToManyField(
        DigitalObject, null=True)

    notes = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='bookcopy_created_by')
    last_modified_by = LastUserField(related_name='bookcopy_last_modified_by')

    class Meta:
        ordering = ['imprint']
        verbose_name = "Book Copy"
        verbose_name_plural = "Book Copies"

    def __unicode__(self):
        return self.imprint.__unicode__()


class Footprint(models.Model):
    book_copy = models.ForeignKey(BookCopy)
    medium = models.CharField(
        "Medium of Evidence", max_length=256,
        help_text='''Where the footprint is derived or deduced from, e.g.
            an extant copy with an owner's signature''')
    provenance = models.CharField(
        "Provenance of Evidence", max_length=256,
        help_text='''Where can one find the evidence now: a particular
        library, archive, a printed book, a journal article etc.''')

    title = models.TextField()
    language = models.ForeignKey(Language, null=True)
    document_type = models.CharField(max_length=256, null=True)
    place = models.ForeignKey(Place, null=True)

    associated_date = models.OneToOneField(ExtendedDateFormat,
                                           null=True)

    call_number = models.CharField(max_length=256, null=True)
    collection = models.ForeignKey(Collection, null=True)

    digital_object = models.ManyToManyField(
        DigitalObject, null=True)

    actor = models.ManyToManyField(
        Actor, null=True,
        help_text="An owner or other person related to this footprint. ")

    notes = models.TextField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='footprint_created_by')
    last_modified_by = LastUserField(related_name='footprint_last_modified_by')

    class Meta:
        ordering = ['title']
        verbose_name = "Footprint"

    def __unicode__(self):
        return self.provenance

    def percent_complete(self):
        required = 11.0  # not including call_number & collection
        complete = 4  # book copy, title, medium & provenance are required

        if self.language is not None:
            complete += 1
        if self.document_type is not None:
            complete += 1
        if self.place is not None:
            complete += 1
        if self.associated_date is not None:
            complete += 1
        if self.digital_object.count() > 0:
            complete += 1
        if self.actor.count() > 0:
            complete += 1
        if self.notes is not None and len(self.notes) > 0:
            complete += 1
        return int(complete/required * 100)

from audit_log.models.fields import CreatingUserField
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.db.models.query_utils import Q
from geoposition import Geoposition

from footprints.batch.validators import validate_date, validate_numeric, \
    validate_latlng
from footprints.main.models import Footprint, Imprint, Role, MEDIUM_CHOICES


class BatchJob(models.Model):
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = CreatingUserField()


class BatchRow(models.Model):

    FIELD_MAPPING = [
        'catalog_url',
        'bhb_number',
        'imprint_title',
        'writtenwork_title',
        'writtenwork_author',
        'writtenwork_author_viaf',
        'writtenwork_author_birth_date',
        'writtenwork_author_death_date',
        'publisher',
        'publisher_viaf',
        'publication_location',
        'publication_date',
        'medium',
        'provenance',
        'call_number',
        'footprint_actor',
        'footprint_actor_viaf',
        'footprint_actor_role',
        'footprint_actor_birth_date',
        'footprint_actor_death_date',
        'footprint_notes',
        'footprint_location',
        'footprint_date'
    ]

    DATE_HELP_TEXT = (
        "This value is invalid. See <a target='_blank' href='"
        "https://github.com/ccnmtl/footprints/wiki/Batch-Import-Format'>"
        "date formats</a> for rules.")
    VIAF_HELP_TEXT = (
        "This value is invalid. "
        "Please enter a numeric VIAF identifier.")
    LOCATION_HELP_TEXT = (
        "This value is invalid. Please enter a geocode, e.g. "
        "51.752021,-1.2577.")
    FOOTPRINT_ACTOR_ROLE_HELP_TEXT = (
        "A role is required when an actor's name is specified. The value is "
        "invalid or missing. See <a target='_blank' "
        "href='https://github.com/ccnmtl/footprints/wiki/Batch-Import-Format'>"
        "roles</a> for a list of choices.")
    IMPRINT_INTEGRITY = (
        "A <a href='/writtenwork/{}/#imprint-{}'>matching imprint</a> "
        "has conflicting data: <b>{}</b>.")
    FOOTPRINT_ACTOR_HELP_TEXT = (
        "An actor name is required when a role is specified.")

    job = models.ForeignKey(BatchJob)

    catalog_url = models.TextField(
        null=True, blank=True, verbose_name='Catalog Link',
        help_text='Please enter a valid url format.')
    bhb_number = models.TextField(
        verbose_name='BHB Number',
        help_text=("This field is required. Please enter a numeric "
                   "BHB identifier."))
    imprint_title = models.TextField(
        verbose_name='Imprint', help_text="This field is required.")
    writtenwork_title = models.TextField(
        null=True, blank=True, verbose_name='Literary Work')
    writtenwork_author = models.TextField(
        null=True, blank=True, verbose_name='Literary Work Author')
    writtenwork_author_viaf = models.TextField(
        null=True, blank=True, verbose_name='Literary Work Author VIAF',
        help_text=VIAF_HELP_TEXT)
    writtenwork_author_birth_date = models.TextField(
        null=True, blank=True, verbose_name='Literary Work Author Birth Date',
        help_text=DATE_HELP_TEXT)
    writtenwork_author_death_date = models.TextField(
        null=True, blank=True, verbose_name='Literary Work Author Death Date',
        help_text=DATE_HELP_TEXT)

    # imprint publisher/printer information
    publisher = models.TextField(
        null=True, blank=True, verbose_name='Publisher')
    publisher_viaf = models.TextField(
        null=True, blank=True, verbose_name='Publisher VIAF',
        help_text=VIAF_HELP_TEXT)
    publication_location = models.TextField(
        null=True, blank=True, verbose_name='Publication Location',
        help_text=LOCATION_HELP_TEXT)
    publication_date = models.TextField(
        null=True, blank=True, help_text=DATE_HELP_TEXT,
        verbose_name='Publication Date')

    medium = models.TextField(
        verbose_name='Evidence Type', help_text='This field is required.')
    provenance = models.TextField(
        verbose_name='Evidence Location', help_text='This field is required.')
    call_number = models.TextField(
        null=True, blank=True, verbose_name='Call Number')

    footprint_actor = models.TextField(
        null=True, blank=True, verbose_name='Footprint Actor',
        help_text=FOOTPRINT_ACTOR_HELP_TEXT)
    footprint_actor_viaf = models.TextField(
        null=True, blank=True, verbose_name='Footprint Actor VIAF',
        help_text=VIAF_HELP_TEXT)
    footprint_actor_role = models.TextField(
        null=True, blank=True, verbose_name='Footprint Actor Role',
        help_text=FOOTPRINT_ACTOR_ROLE_HELP_TEXT)
    footprint_actor_birth_date = models.TextField(
        null=True, blank=True, verbose_name='Footprint Actor Birth Date',
        help_text=DATE_HELP_TEXT)
    footprint_actor_death_date = models.TextField(
        null=True, blank=True, verbose_name='Footprint Actor Death Date',
        help_text=DATE_HELP_TEXT)
    footprint_notes = models.TextField(
        null=True, blank=True, verbose_name='Footprint Notes')
    footprint_location = models.TextField(
        null=True, blank=True, verbose_name='Footprint Location',
        help_text=LOCATION_HELP_TEXT)
    footprint_date = models.TextField(
        null=True, blank=True, verbose_name='Footprint Date',
        help_text=DATE_HELP_TEXT)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['writtenwork_title', 'imprint_title', 'id']

    @classmethod
    def imported_fields(cls):
        return [BatchRow._meta.get_field(name) for name in cls.FIELD_MAPPING]

    def aggregate_notes(self):
        notes = ''
        if self.catalog_url and len(self.catalog_url) > 0:
            notes = u'{}<br />{}'.format(
                self.catalog_url, self.footprint_notes)
        else:
            notes = self.footprint_notes

        return notes

    def get_writtenwork_title(self):
        if self.writtenwork_title is None or len(self.writtenwork_title) < 1:
            return self.imprint_title
        return self.writtenwork_title

    def check_imprint_integrity(self):
        msg = None

        imprint = Imprint.objects.filter(
            standardized_identifier__identifier=self.bhb_number).first()

        if imprint is None:
            return msg

        fields = []

        # title, date, location & writtenwork title should match
        if imprint.title != self.imprint_title:
            fields.append('title')

        if not imprint.publication_date.match_string(
                self.publication_date):
            fields.append('publication date')

        if not imprint.place.match_string(self.publication_location):
            fields.append('publication location')

        if (self.writtenwork_title and
                imprint.work.title.lower() != self.writtenwork_title.lower()):
            fields.append('literary work title')

        if len(fields):
            msg = self.IMPRINT_INTEGRITY.format(
                imprint.work.id, imprint.id, ', '.join(fields))

        return msg

    def similar_footprints(self):
        kwargs = {
            'medium': self.medium,
            'provenance': self.provenance,
            'call_number': self.call_number,
            'notes': self.aggregate_notes(),
            'book_copy__imprint__work__title__iexact':
                self.get_writtenwork_title()
        }

        bhb = self.bhb_number
        args = [
            Q(book_copy__imprint__standardized_identifier__identifier=bhb) |
            Q(book_copy__imprint__title__iexact=self.imprint_title)
        ]

        author = self.writtenwork_author
        if author:
            args.append(
                Q(book_copy__imprint__work__actor__person__name=author) |
                Q(book_copy__imprint__work__actor__alias=author))

        if self.publisher:
            args.append(
                Q(book_copy__imprint__actor__person__name=self.publisher) |
                Q(book_copy__imprint__actor__alias=self.publisher))

        if (self.publication_location and
                self.validate_publication_location()):
            latlong = self.publication_location.split(',')
            gp = Geoposition(latlong[0].strip(), latlong[1].strip())
            kwargs['book_copy__imprint__place__position'] = gp

        if self.footprint_actor:
            args.append(
                Q(actor__person__name=self.footprint_actor) |
                Q(actor__alias=self.footprint_actor))

        if (self.footprint_location and
                self.validate_footprint_location()):
            latlong = self.footprint_location.split(',')
            kwargs['place__position'] = Geoposition(latlong[0], latlong[1])

        qs = Footprint.objects.filter(*args, **kwargs)
        return qs.values_list('id', flat=True)

    def validate_catalog_url(self):
        try:
            if self.catalog_url:
                URLValidator()(self.catalog_url)
            return True
        except ValidationError:
            return False

    def validate_bhb_number(self):
        return validate_numeric(self.bhb_number)

    def validate_writtenwork_author_viaf(self):
        return validate_numeric(self.writtenwork_author_viaf)

    def validate_writtenwork_author_birth_date(self):
        return validate_date(self.writtenwork_author_birth_date)

    def validate_writtenwork_author_death_date(self):
        return validate_date(self.writtenwork_author_death_date)

    def validate_publisher_viaf(self):
        return validate_numeric(self.publisher_viaf)

    def validate_publication_date(self):
        return validate_date(self.publication_date)

    def validate_publication_location(self):
        return validate_latlng(self.publication_location)

    def validate_medium(self):
        if not self.medium:
            return True

        return self.medium in MEDIUM_CHOICES

    def validate_footprint_actor(self):
        # if role is specified, actor must be specified
        if self.footprint_actor_role and not self.footprint_actor:
            return False

        return True

    def validate_footprint_actor_viaf(self):
        return validate_numeric(self.footprint_actor_viaf)

    def validate_footprint_actor_birth_date(self):
        return validate_date(self.footprint_actor_birth_date)

    def validate_footprint_actor_death_date(self):
        return validate_date(self.footprint_actor_death_date)

    def validate_footprint_date(self):
        return validate_date(self.footprint_date)

    def validate_footprint_actor_role(self):
        # if actor is specified, role must be specified
        if self.footprint_actor and not self.footprint_actor_role:
            return False

        if not self.footprint_actor_role:
            return True

        # role must be known
        return Role.objects.for_footprint().filter(
            name=self.footprint_actor_role).exists()

    def validate_footprint_location(self):
        return validate_latlng(self.footprint_location)

from audit_log.models.fields import CreatingUserField
from django.db import models

from footprints.main.models import Footprint


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
        "This date format is invalid. See <a target='_blank' href='"
        "https://github.com/ccnmtl/footprints/wiki/Batch-Import-Format'>"
        "date formats</a> for rules")

    job = models.ForeignKey(BatchJob)

    catalog_url = models.TextField(
        null=True, blank=True, verbose_name='Catalog Link',
        help_text='Please enter a valid url format')
    bhb_number = models.TextField(
        verbose_name='BHB Number', help_text='This field is required')
    imprint_title = models.TextField(
        verbose_name='Imprint')
    writtenwork_title = models.TextField(
        null=True, blank=True, verbose_name='Literary Work')
    writtenwork_author = models.TextField(
        null=True, blank=True, verbose_name='Literary Work Author')
    writtenwork_author_viaf = models.TextField(
        null=True, blank=True, verbose_name='Literary Work Author VIAF')
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
        null=True, blank=True, verbose_name='Publisher VIAF')
    publication_location = models.TextField(
        null=True, blank=True, verbose_name='Publication Location')
    publication_date = models.TextField(
        null=True, blank=True, help_text=DATE_HELP_TEXT,
        verbose_name='Publication Date')

    medium = models.TextField(
        verbose_name='Evidence Type', help_text='This field is required')
    provenance = models.TextField(
        verbose_name='Evidence Location', help_text='This field is required')
    call_number = models.TextField(
        null=True, blank=True, verbose_name='Call Number')

    footprint_actor = models.TextField(
        null=True, blank=True, verbose_name='Footprint Actor')
    footprint_actor_viaf = models.TextField(
        null=True, blank=True, verbose_name='Footprint Actor VIAF')
    footprint_actor_role = models.TextField(
        null=True, blank=True, verbose_name='Footprint Actor Role')
    footprint_actor_birth_date = models.TextField(
        null=True, blank=True, verbose_name='Footprint Actor Birth Date',
        help_text=DATE_HELP_TEXT)
    footprint_actor_death_date = models.TextField(
        null=True, blank=True, verbose_name='Footprint Actor Death Date',
        help_text=DATE_HELP_TEXT)
    footprint_notes = models.TextField(
        null=True, blank=True, verbose_name='Footprint Notes')
    footprint_location = models.TextField(
        null=True, blank=True, verbose_name='Footprint Location')
    footprint_date = models.TextField(
        null=True, blank=True, verbose_name='Footprint Date',
        help_text=DATE_HELP_TEXT)

    created_at = models.DateTimeField(auto_now_add=True)

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

    def check_for_duplication(self):
        # 1st pass: duplicate medium, provenance, call_number, notes
        # imprint title, written work title
        matches = Footprint.objects.filter(
            medium=self.medium, provenance=self.provenance,
            call_number=self.call_number, notes=self.aggregate_notes(),
            book_copy__imprint__title=self.imprint_title,
            book_copy__imprint__work__title=self.writtenwork_title)

        # @todo - 2nd pass:
        # ['bhb_number', 'writtenwork_author', 'publisher',
        #  'publication_location', 'publication_date',
        #  'footprint_actor', 'footprint_actor_role',
        # 'footprint_location', 'footprint_date'

        return matches.exists()

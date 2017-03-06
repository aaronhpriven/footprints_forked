from django import template
from django.db.models.query_utils import Q


register = template.Library()


def flag_percent_complete(fp):
    return fp.percent_complete < 50


def flag_empty_narrative(fp):
    return not fp.narrative


def flag_empty_call_number(fp):
    return (fp.medium == 'Bookseller/auction catalog (1850-present)' and
            not fp.call_number)


def flag_empty_bhb_number(fp):
    return not fp.book_copy.imprint.has_bhb_number()


@register.simple_tag
def has_moderation_flags(fp):
    return len(moderation_flags(fp)) > 0


@register.simple_tag
def moderation_flags(fp):
    errors = []
    if flag_empty_call_number(fp):
        errors.append('Catalog\'s call number is empty')

    if flag_empty_bhb_number(fp):
        errors.append('Imprint has no BHB number')

    if flag_empty_narrative(fp):
        errors.append('Narrative is empty')

    if flag_percent_complete(fp):
        errors.append('Percent complete is less than 50%')

    return errors


def moderation_footprints():
    from footprints.main.models import Footprint, SLUG_BHB
    qs = Footprint.objects.exclude(verified=True).filter(
        Q(percent_complete__lt=50) |
        Q(narrative__isnull=True) |
        Q(medium='Bookseller/auction catalog (1850-present)',
          call_number__isnull=True) |
        ~Q(book_copy__imprint__standardized_identifier__identifier_type__slug=SLUG_BHB))  # noqa:251
    return qs.select_related(
        'created_by', 'last_modified_by',
        'book_copy__imprint').prefetch_related(
        'book_copy__imprint__standardized_identifier__identifier_type')
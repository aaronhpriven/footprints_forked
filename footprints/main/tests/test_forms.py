from django.test.testcases import TestCase

from footprints.main.forms import FootprintSearchForm, ContactUsForm, \
    ExtendedDateForm
from footprints.main.models import ExtendedDate


class FootprintSearchFormTest(TestCase):

    def test_empty_search(self):
        form = FootprintSearchForm()
        sqs = form.search()
        self.assertEquals(sqs.count(), 0)

    def test_form_clean_empty(self):
        form = FootprintSearchForm()
        form._errors = {}
        form.cleaned_data = {
            'q': '',
            'search_level': True,
            'footprint_start_year': None,
            'footprint_end_year': None
        }

        form.clean()
        self.assertEquals(len(form._errors.keys()), 1)
        self.assertTrue('q' in form._errors)

    def test_form_clean_q(self):
        form = FootprintSearchForm()
        form._errors = {}
        form.cleaned_data = {
            'q': 'oppenheim',
            'footprint_start_year': None,
            'footprint_end_year': None
        }

        form.clean()
        self.assertEquals(len(form._errors.keys()), 0)

    def test_form_clean_errors_future_date(self):
        form = FootprintSearchForm()
        form._errors = {}
        form.cleaned_data = {
            'q': '',
            'footprint_start_year': 2080,
            'footprint_end_year': 2080
        }

        form.clean()
        self.assertEquals(len(form._errors.keys()), 2)
        self.assertTrue('footprint_start_year' in form._errors)
        self.assertTrue('footprint_end_year' in form._errors)

    def test_form_clean_errors_past_date(self):
        form = FootprintSearchForm()
        form._errors = {}
        form.cleaned_data = {
            'q': '',
            'footprint_start_year': 999,
            'footprint_end_year': 999
        }

        form.clean()
        self.assertEquals(len(form._errors.keys()), 2)
        self.assertTrue('footprint_start_year' in form._errors)
        self.assertTrue('footprint_end_year' in form._errors)

    def test_form_clean_range(self):
        form = FootprintSearchForm()
        form._errors = {}
        form.cleaned_data = {
            'q': '',
            'footprint_range': '1',
            'footprint_start_year': 2016,
            'footprint_end_year': 1740
        }

        form.clean()
        self.assertEquals(len(form._errors.keys()), 1)
        self.assertTrue('footprint_start_year' in form._errors)

    def test_form_clean_single_year_valid(self):
        form = FootprintSearchForm()
        form._errors = {}
        form.cleaned_data = {
            'q': '',
            'footprint_range': '0',
            'footprint_start_year': 1740,
            'footprint_end_year': None
        }

        form.clean()
        self.assertEquals(len(form._errors.keys()), 0)

    def test_form_clean_range_valid(self):
        form = FootprintSearchForm()
        form._errors = {}
        form.cleaned_data = {
            'q': '',
            'footprint_range': '1',
            'footprint_start_year': None,
            'footprint_end_year': 1740
        }

        form.clean()
        self.assertEquals(len(form._errors.keys()), 0)


class ContactUsFormTest(TestCase):

    def test_form_clean(self):
        form = ContactUsForm()
        form._errors = {}
        form.cleaned_data = {
            'decoy': '',
            'subject': 'other'
        }

        form.clean()
        self.assertEquals(len(form._errors.keys()), 0)

    def test_form_clean_errors(self):
        form = ContactUsForm()
        form._errors = {}
        form.cleaned_data = {
            'decoy': 'foo',
            'subject': '-----'
        }

        form.clean()
        self.assertEquals(len(form._errors.keys()), 2)
        self.assertTrue('decoy' in form._errors)
        self.assertTrue('subject' in form._errors)


class ExtendedDateFormTest(TestCase):

    def test_get_attr(self):
        form = ExtendedDateForm()
        form.cleaned_data = {'attr': 'foo'}
        self.assertEquals(form.get_attr(), 'foo')

    def test_clean_empty_fields(self):
        data = {
            'is_range': True,
            'millenium1': None, 'century1': '0', 'decade1': '1', 'year1': '0',
            'month1': '1', 'day1': '1',
            'approximate1': True, 'uncertain1': True,
            'millenium2': None, 'century2': '0', 'decade2': None, 'year2': '1',
            'month2': None, 'day2': None,
            'approximate2': False, 'uncertain2': False,
        }
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.get_error_messages(),
                          u'Please fill out all required fields<br />')

        data['millenium1'] = 2
        data['millenium2'] = 2
        ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.get_error_messages(),
                          u'Please fill out all required fields<br />')

    def test_clean_valid_date(self):
        data = {
            'is_range': False,
            'millenium1': '2', 'century1': '0', 'decade1': '1', 'year1': '0',
            'month1': '2', 'day1': '28',
            'approximate1': True, 'uncertain1': True,
            'millenium2': None, 'century2': None, 'decade2': None,
            'year2': None, 'month2': None, 'day2': None,
            'approximate2': False, 'uncertain2': False,
        }
        form = ExtendedDateForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEquals(ExtendedDate.objects.count(), 0)

    def test_clean_valid_date_range(self):
        data = {
            'is_range': True,
            'millenium1': '2', 'century1': '0', 'decade1': '1', 'year1': '0',
            'month1': '2', 'day1': '28',
            'approximate1': True, 'uncertain1': True,
            'millenium2': '2', 'century2': '0', 'decade2': '1', 'year2': '2',
            'month2': '2', 'day2': '29',
            'approximate2': False, 'uncertain2': False,
        }
        form = ExtendedDateForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEquals(form.get_error_messages(), '')
        self.assertEquals(ExtendedDate.objects.count(), 0)

        dt = form.save()
        self.assertEquals(ExtendedDate.objects.count(), 1)
        self.assertEquals(dt.edtf_format, '2010-02-28?~/2012-02-29')

    def test_clean_invalid_date(self):
        data = {
            'is_range': False,
            'millenium1': '2', 'century1': '2', 'decade1': '1', 'year1': '0',
            'month1': '2', 'day1': '31',
            'approximate1': True, 'uncertain1': True,
            'millenium2': None, 'century2': None, 'decade2': None,
            'year2': None, 'month2': None, 'day2': None,
            'approximate2': False, 'uncertain2': False,
        }
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.get_error_messages(),
                          u'Please specify a valid date<br />')

        data['day1'] = 28
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.get_error_messages(),
                          u'The date must be today or earlier<br />')

    def test_clean_invalid_date_ranges(self):
        data = {
            'is_range': True,
            'millenium1': '2', 'century1': '2', 'decade1': '1', 'year1': '0',
            'month1': '6', 'day1': '31',
            'approximate1': True, 'uncertain1': True,
            'millenium2': '2', 'century2': '2', 'decade2': '0', 'year2': '9',
            'month2': '9', 'day2': '31',
            'approximate2': False, 'uncertain2': False,
        }

        # invalid start date
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.get_error_messages(),
                          u'Please specify a valid start date<br />')
        self.assertEquals(ExtendedDate.objects.count(), 0)

        # invalid end date
        data['day1'] = '30'
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.get_error_messages(),
            u'Please specify a valid end date<br />')
        self.assertEquals(ExtendedDate.objects.count(), 0)

        # start year in the future
        data['day2'] = 30
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.get_error_messages(),
                          u'All dates must be today or earlier<br />')
        self.assertEquals(ExtendedDate.objects.count(), 0)

        # end year in the future
        data['century1'] = 0
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(form.get_error_messages(),
                          u'All dates must be today or earlier<br />')
        self.assertEquals(ExtendedDate.objects.count(), 0)

        # start > end
        data['century2'] = 0
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertEquals(
            form.get_error_messages(),
            u'The start date must be earlier than the end date.<br />')
        self.assertEquals(ExtendedDate.objects.count(), 0)

    def test_clean_incomplete_data(self):
        data = {
            'approximate1': True, 'approximate2': False, 'attr': u'',
            'century1': None, 'century2': None, 'day1': None, 'day2': None,
            'decade1': None, 'decade2': None, 'is_range': False,
            'millenium1': 1, 'millenium2': None,
            'month1': None, 'month2': None,
            'uncertain1': True, 'uncertain2': False,
            'year1': None, 'year2': None
        }
        form = ExtendedDateForm(data=data)
        self.assertFalse(form.is_valid())

        self.assertEquals(form.get_error_messages(),
                          u'Please specify a valid date<br />')

import urllib

from django import forms
from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _
from haystack.forms import ModelSearchForm
from haystack.utils import get_model_ct

from footprints.main.models import Footprint, Role, DigitalObject, \
    ExtendedDateFormat, Language, DigitalFormat, \
    StandardizedIdentification, Person, Actor, Place, Collection, \
    WrittenWork, Imprint, BookCopy


class RoleForm(ModelForm):
    class Meta:
        model = Role


class ExtendedDateFormatForm(ModelForm):
    class Meta:
        model = ExtendedDateFormat


class LanguageForm(ModelForm):
    class Meta:
        model = Language


class DigitalFormatForm(ModelForm):
    class Meta:
        model = DigitalFormat


class DigitalObjectForm(ModelForm):
    class Meta:
        model = DigitalObject
        fields = ['name', 'file', 'description']


class StandardizedIdentificationForm(ModelForm):
    class Meta:
        model = StandardizedIdentification


class PersonForm(ModelForm):

    last_name = forms.CharField(max_length=256)
    first_name = forms.CharField(max_length=256)
    middle_name = forms.CharField(max_length=256)
    suffix = forms.CharField(max_length=256)

    date_of_birth = forms.CharField(widget=forms.TextInput(),
                                    max_length=256)

    class Meta:
        model = Person
        fields = ['last_name', 'first_name', 'middle_name', 'suffix',
                  'date_of_birth', 'standardized_identifier',
                  'digital_object', 'notes']


class ActorForm(ModelForm):
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        widget=forms.Select(attrs={'class': 'add-another'}))

    person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        widget=forms.Select(attrs={'class': 'add-another'}))

    last_name = forms.CharField(max_length=256)
    first_name = forms.CharField(max_length=256)
    middle_name = forms.CharField(max_length=256)
    suffix = forms.CharField(max_length=256)

    class Meta:
        model = Actor
        fields = ['person', 'role', 'last_name', 'first_name',
                  'middle_name', 'suffix']


class PlaceForm(ModelForm):
    class Meta:
        model = Place
        fields = ['position']


class CollectionForm(ModelForm):
    class Meta:
        model = Collection


class WrittenWorkForm(ModelForm):
    class Meta:
        model = WrittenWork


class ImprintForm(ModelForm):
    publication_date = forms.CharField(widget=forms.TextInput(),
                                       max_length=256)

    class Meta:
        model = Imprint


class BookCopyForm(ModelForm):
    class Meta:
        model = BookCopy


class FootprintForm(ModelForm):
    recorded_date = forms.CharField(widget=forms.TextInput(),
                                    max_length=256)

    class Meta:
        model = Footprint


class FootprintSearchForm(ModelSearchForm):
    def __init__(self, *args, **kwargs):
        super(FootprintSearchForm, self).__init__(*args, **kwargs)

        choices = [
            (get_model_ct(Footprint), 'Footprint'),
            (get_model_ct(WrittenWork), 'Written Work'),
        ]
        self.fields['models'] = forms.MultipleChoiceField(
            choices=choices, required=False, label=_('Search By Record Type'),
            widget=forms.CheckboxSelectMultiple(
                attrs={'class': 'regDropDown'}))
        self.fields['q'].widget.attrs['class'] = 'form-control'
        self.fields['q'].widget.attrs['placeholder'] = 'Titles, People, Places'

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        if not self.cleaned_data.get('q'):
            sqs = self.searchqueryset.all()
        else:
            sqs = self.searchqueryset.auto_query(self.cleaned_data['q'])

        sqs = sqs.exclude(django_ct__in=["main.imprint",
                                         "main.place",
                                         "main.person"])

        if self.load_all:
            sqs = sqs.load_all()

        sqs = sqs.models(*self.get_models())
        sqs = sqs.order_by('sort_by')
        return sqs

    def get_query_params(self):
        return urllib.urlencode(self.cleaned_data, doseq=True)

SUBJECT_CHOICES = (
    ('-----', '-----'),
    ('info', 'Request more information'),
    ('contribute', 'Learn more about how to contribute'),
    ('bug', 'Correction or bug report'),
    ('other', 'Other (please specify)')
)


class ContactUsForm(forms.Form):
    name = forms.CharField(required=True, max_length=512)
    email = forms.EmailField(required=True)

    subject = forms.ChoiceField(
        required=True, choices=SUBJECT_CHOICES,
        widget=forms.Select(attrs={'class': "form-control"}))

    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': "form-control"}),
        required=True)

    decoy = forms.CharField(widget=forms.Textarea, required=False)

    def clean(self):
        cleaned_data = super(ContactUsForm, self).clean()

        if cleaned_data['subject'] == '-----':
            self._errors["subject"] = self.error_class([
                "Please specify a subject"])

        if 'decoy' in cleaned_data and len(cleaned_data['decoy']) > 0:
            self._errors["decoy"] = self.error_class([
                "Please leave this field blank"])

        return cleaned_data

from django.db.utils import IntegrityError
from django.test import TestCase

from footprints.main.models import Language, DigitalFormat, \
    ExtendedDateFormat, StandardizedIdentification, \
    Actor, Imprint, FOOTPRINT_LEVEL, IMPRINT_LEVEL, WRITTENWORK_LEVEL, Role
from footprints.main.tests.factories import RoleFactory, \
    ActorFactory, PlaceFactory, CollectionFactory, \
    WrittenWorkFactory, ImprintFactory, BookCopyFactory, FootprintFactory, \
    PersonFactory


class BasicModelTest(TestCase):

    def test_fuzzy_date(self):
        a_date = ExtendedDateFormat.objects.create(edtf_format='2004?-06-11')
        self.assertEquals(a_date.__unicode__(), '2004?-06-11')

    def test_language(self):
        language = Language.objects.create(name='English')
        self.assertEquals(language.__unicode__(), 'English')

        try:
            Language.objects.create(name='English')
            self.fail('expected an already exists error')
        except IntegrityError:
            pass  # expected

    def test_role(self):
        owner = RoleFactory(name="Owner", level=FOOTPRINT_LEVEL)
        publisher = RoleFactory(name="Publisher", level=IMPRINT_LEVEL)
        author = RoleFactory(name="Author", level=WRITTENWORK_LEVEL)

        self.assertEquals(author, Role.objects.get_author_role())
        self.assertEquals(owner, Role.objects.get_owner_role())

        qs = Role.objects.for_footprint()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), owner)

        qs = Role.objects.for_imprint()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), publisher)

        qs = Role.objects.for_work()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), author)

    def for_footprint(self):
        return self.filter(level=FOOTPRINT_LEVEL)

    def for_imprint(self):
        return self.filter(level=IMPRINT_LEVEL)

    def for_work(self):
        return self.filter(level=WRITTENWORK_LEVEL)

    def test_digital_format(self):
        digital_format = DigitalFormat.objects.create(name='png')
        self.assertEquals(digital_format.__unicode__(), 'png')

        try:
            DigitalFormat.objects.create(name='png')
            self.fail('expected an already exists error')
        except IntegrityError:
            pass  # expected

    def test_standardized_identification(self):
        si = StandardizedIdentification.objects.create(identifier='foo',
                                                       identifier_type='LOC')

        self.assertEquals(si.__unicode__(), 'foo')

        si = StandardizedIdentification.objects.create(
            identifier='bar', identifier_type='BHB',
            identifier_text='Barish')

        self.assertEquals(si.__unicode__(),
                          'bar')

    def test_person(self):
        person = PersonFactory(name='Cicero')
        self.assertEquals(person.__unicode__(), "Cicero")

    def test_actor(self):
        person = PersonFactory()
        role = RoleFactory()
        actor = Actor.objects.create(person=person, role=role)

        # No Alternate Name
        self.assertEquals(
            actor.__unicode__(),
            '%s (%s)' % (actor.person.name, role.name))

        # With Alternate Name
        actor = ActorFactory(role=role)
        self.assertEquals(
            actor.__unicode__(),
            '%s as %s (%s)' % (actor.person.name, actor.alias, role.name))

    def test_place(self):
        place = PlaceFactory()
        self.assertEquals(place.__unicode__(),
                          'Smyrna, Greece')

    def test_collection(self):
        collection = CollectionFactory(name='The Morgan Collection')
        self.assertEquals(collection.__unicode__(), 'The Morgan Collection')

    def test_written_work(self):
        work = WrittenWorkFactory()
        self.assertEquals(work.__unicode__(), 'The Odyssey')

    def test_imprint(self):
        imprint = Imprint.objects.create(work=WrittenWorkFactory())
        self.assertEquals(imprint.__unicode__(), 'The Odyssey')

        imprint = ImprintFactory()
        self.assertEquals(imprint.__unicode__(),
                          'The Odyssey, Edition 1 (1984~)')

    def test_book_copy(self):
        copy = BookCopyFactory()
        self.assertTrue(
            copy.__unicode__().endswith('The Odyssey, Edition 1 (1984~)'))

    def test_footprint(self):
        footprint = FootprintFactory()
        self.assertEquals(footprint.__unicode__(), 'Provenance')

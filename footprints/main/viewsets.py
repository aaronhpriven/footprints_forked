from django.contrib.auth.models import User
from rest_framework import viewsets

from footprints.main.models import (
    Footprint, Actor, Person, Role, WrittenWork, Language, ExtendedDateFormat,
    Place, Imprint, BookCopy, StandardizedIdentification, DigitalFormat,
    DigitalObject)
from footprints.main.permissions import IsStaffOrReadOnly
from footprints.main.serializers import (
    FootprintSerializer, LanguageSerializer, RoleSerializer,
    ExtendedDateFormatSerializer, ActorSerializer, PersonSerializer,
    PlaceSerializer, WrittenWorkSerializer, UserSerializer, ImprintSerializer,
    BookCopySerializer, StandardizedIdentificationSerializer,
    DigitalFormatSerializer, DigitalObjectSerializer)


class FootprintViewSet(viewsets.ModelViewSet):
    queryset = Footprint.objects.all()
    serializer_class = FootprintSerializer
    permission_classes = (IsStaffOrReadOnly,)


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = (IsStaffOrReadOnly,)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = (IsStaffOrReadOnly,)


class ExtendedDateFormatViewSet(viewsets.ModelViewSet):
    queryset = ExtendedDateFormat.objects.all()
    serializer_class = ExtendedDateFormatSerializer
    permission_classes = (IsStaffOrReadOnly,)


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = (IsStaffOrReadOnly,)


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = (IsStaffOrReadOnly,)


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = (IsStaffOrReadOnly,)


class WrittenWorkViewSet(viewsets.ModelViewSet):
    queryset = WrittenWork.objects.all()
    serializer_class = WrittenWorkSerializer
    permission_classes = (IsStaffOrReadOnly,)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsStaffOrReadOnly,)


class ImprintViewSet(viewsets.ModelViewSet):
    model = Imprint
    serializer_class = ImprintSerializer
    permission_classes = (IsStaffOrReadOnly,)

    def get_queryset(self):
        qs = Imprint.objects.all()

        work_id = self.request.GET.get('work', None)
        if work_id:
            qs = qs.filter(work__id=work_id)

        return qs


class BookCopyViewSet(viewsets.ModelViewSet):
    model = BookCopy
    serializer_class = BookCopySerializer
    permission_classes = (IsStaffOrReadOnly,)

    def get_queryset(self):
        qs = BookCopy.objects.all()

        imprint_id = self.request.GET.get('imprint', None)
        if imprint_id:
            qs = qs.filter(imprint__id=imprint_id)

        return qs


class StandardizedIdentificationViewSet(viewsets.ModelViewSet):
    queryset = StandardizedIdentification.objects.all()
    serializer_class = StandardizedIdentificationSerializer
    permission_classes = (IsStaffOrReadOnly,)


class DigitalFormatViewSet(viewsets.ModelViewSet):
    queryset = DigitalFormat.objects.all()
    serializer_class = DigitalFormatSerializer
    permission_classes = (IsStaffOrReadOnly,)


class DigitalObjectViewSet(viewsets.ModelViewSet):
    queryset = DigitalObject.objects.all()
    serializer_class = DigitalObjectSerializer
    permission_classes = (IsStaffOrReadOnly,)

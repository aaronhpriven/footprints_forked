from itertools import chain

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import logout as auth_logout_view
from django.views.generic.base import TemplateView, View
from djangowind.views import logout as wind_logout_view
from haystack.query import SearchQuerySet
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONPRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from footprints.main.models import Actor, Footprint, Imprint, WrittenWork
from footprints.main.serializers import ActorSerializer, TitleSerializer
from footprints.mixins import JSONResponseMixin, LoggedInMixin, \
    LoggedInStaffMixin


class IndexView(TemplateView):
    template_name = "main/index.html"


class LoginView(JSONResponseMixin, View):

    def post(self, request):
        request.session.set_test_cookie()
        login_form = AuthenticationForm(request, request.POST)
        if login_form.is_valid():
            login(request, login_form.get_user())
            if request.user is not None:
                next_url = request.POST.get('next', '/')
                return self.render_to_json_response({'next': next_url})

        return self.render_to_json_response({'error': True})


class LogoutView(LoggedInMixin, View):

    def get(self, request):
        if hasattr(settings, 'CAS_BASE'):
            return wind_logout_view(request, next_page="/")
        else:
            return auth_logout_view(request, "/")


class RecordWorkspaceView(LoggedInStaffMixin, TemplateView):
    template_name = "record/workspace.html"

    def get_context_data(self, **kwargs):
        return {}


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class TitleListView(APIView):
    renderer_classes = (JSONPRenderer,)
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        sqs = SearchQuerySet().autocomplete(
            title_auto=request.GET.get('q', ''))
        serializer = TitleSerializer(sqs, many=True)
        return Response(serializer.data)

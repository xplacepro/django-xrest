from django.conf.urls import url

from xrest.views import BaseApiView

from .forms import CreateForm, UpdateForm
from .models import TestModel


class TestApi(BaseApiView):
    model = TestModel
    update_form = UpdateForm
    create_form = CreateForm
    api_name = 'test'

    def post__test_url(self, request, *args, **kwargs):
        return self.response({
            'test': 'test'
        })

    @classmethod
    def urls(cls):
        urls = super(TestApi, cls).urls()
        urls += [
            url(r'^(?P<pk>[0-9]*)/$', cls.as_view(
                handlers_dict={'post': 'post__test_url'}), name='test'),
        ]
        return urls

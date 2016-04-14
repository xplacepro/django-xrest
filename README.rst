==================================================
XRest api - Minimalistic rest framework for django
==================================================

Installation
------------

pip install git+git://github.com/xplacepro/django-xrest.git


Usage
-----

Api class
=========

First declare some api class. This gives you base CRUD api endpoints for given model.

.. code-block:: python

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

        # you can add method by overriding urls method classmethod
        @classmethod
        def urls(cls):
            urls = super(TestApi, cls).urls()
            urls += [
                url(r'^(?P<pk>[0-9]*)/test/$', cls.as_view(
                    handlers_dict={'post': 'post__test_url'}), name='test'),
            ]
            return urls


Urls
====

Then register this class by doing this in your urls.py

.. code-block:: python

    from xrest_test.testapp.api import TestApi
    from xrest.api import Api

    api_v1 = Api(version='1.0')
    api_v1.register(TestApi)

    urlpatterns = [
        url(r'^admin/', admin.site.urls),

        url(r'^api/', include(api_v1)),

    ]


This gives you 5 api endpoints. 4 of them are base crud operations plus one custom defined.

POST /api/1.0/test/ - Creation

GET /api/1.0/test/ - Listing

GET /api/1.0/test/{id}/ - Get Item

POST /api/1.0/test/{id}/ - Update item

POST /api/1.0/test/{id}/test/ - Custom method
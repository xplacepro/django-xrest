from django.conf.urls import url, include


class Api(object):
    def __init__(self, version='1.0'):
        self.version = version
        self.urlpatterns = []

    def register(self, api_cls):
        self.urlpatterns += [url(r'{0}/{1}/'.format(
            api_cls.api_name, self.version), include(api_cls.urls(), namespace=api_cls.api_name))]


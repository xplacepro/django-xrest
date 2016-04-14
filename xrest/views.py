import json

from django.conf.urls import url
from django.views.generic import View
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction

from .paginator import LimitOffsetPaginator
from .exceptions import ResponseException
from .authentication import NoAuthentication


class BaseApiView(View):
    """
    Base api view, which encapsulates crud methods, validates post data, and sets content_type
    """
    create_form = None
    update_form = None
    model = None
    object = None
    api_name = None
    content_type = 'application/json'
    data = None
    paginator = LimitOffsetPaginator
    authentication = NoAuthentication()
    skip_authentication = []
    object_pk = 'pk'
    handlers_dict = None

    def get_update_form(self):
        return self.update_form

    def get_create_form(self):
        return self.create_form

    def get_queryset(self):
        return self.model.objects.all()

    def object_not_found(self):
        """
        404 response
        :return:
        """
        return ResponseException({'error': 'object_not_found'}, status=404)

    def get_object(self, object_pk):
        try:
            object_pk = int(object_pk)
        except (ValueError, TypeError):
            pass
        try:
            return self.get_queryset().get(**{self.object_pk: object_pk})
        except self.model.DoesNotExist:
            raise self.object_not_found()

    def error(self, data, status=400):
        return self.response(data, status=status, resp_type='error')

    def response(self, data, status=200, resp_type='sync'):
        """
        Success response which dumps data to json
        :param data:
        :param status:
        :param resp_type:
        :return:
        """
        resp = {
            'type': resp_type,
            'status': status,
            'metadata': data
        }
        return HttpResponse(json.dumps(resp), content_type=self.content_type, status=status)

    def make_object_dict(self, obj):
        data = obj.to_json_dict()
        return data

    def validate_form(self, form, request=None):
        setattr(form, 'request', request or self.request)
        if not form.is_valid():
            errors = {}
            for k, err in form.errors.items():
                errors[k] = err[0]

            raise ResponseException({'errors': errors}, 400)
        return form.cleaned_data

    @transaction.atomic()
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        """
        Overridden Dispatcher, that handler request
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        request_method = request.method.lower()

        handler_name = self.handlers_dict.get(request_method, None)

        handler = self.http_method_not_allowed

        if request_method in self.http_method_names:
            try:
                handler = getattr(self, handler_name, self.http_method_not_allowed)
            except TypeError:
                pass

        if handler_name not in self.skip_authentication:
            user = self.authentication.authenticate(request)
            if user is None:
                return self.response({'error': 'unauthorized'}, status=401)

        try:
            pk_kw = self.object_pk in kwargs.keys()
            if pk_kw:
                object_pk = kwargs.get(self.object_pk, None)
                self.object = self.get_object(object_pk)

            if request_method in ['post', 'put', 'delete', 'patch']:
                try:
                    data = request.body.decode()
                    if data:
                        data = json.loads(request.body.decode())
                    else:
                        data = {}
                    self.data = data
                except ValueError:
                    return self.response({'error': 'invalid_data'}, status=400)

            return handler(request, *args, **kwargs)

        except ResponseException as exc:
            return self.error(exc.error_dict, exc.status)

        # return wrapper

    def get__list(self, request, *args, **kwargs):
        """
        Base list method
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        objects = self.get_queryset()

        paginator = self.paginator(request, objects)
        if paginator.errors:
            raise ResponseException({'errors': paginator.errors}, 400)

        meta = paginator.meta()
        objects = [self.make_object_dict(obj) for obj in paginator.sliced_queryset]
        response = {'objects': objects}
        response.update({'pagination': meta})

        return self.response(response)

    def create_object(self):
        form_cls = self.get_create_form()
        form = form_cls(self.data)
        self.validate_form(form, request=self.request)
        form.save()
        return form.instance

    def post__list(self, request, *args, **kwargs):
        """
        Base create method
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        self.object = self.create_object()
        return self.response({'object': self.make_object_dict(self.object)})

    def update_object(self):
        form_cls = self.get_update_form()
        form = form_cls(self.data, instance=self.object)
        self.validate_form(form, request=self.request)
        form.save()
        return form.cleaned_data

    def post__object(self, request, *args, **kwargs):
        """
        Base update object method
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        if not self.get_update_form():
            return self.error({'error': 'method_not_allowed'}, status=405)
        self.update_object()
        return self.response({'object': self.make_object_dict(self.object)})

    def get__object(self, request, *args, **kwargs):
        """
        Base get object method
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return self.response({'object': self.make_object_dict(self.object)})

    def delete__object(self, request, *args, **kwargs):
        """
        Base delete object method
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        self.object.delete()
        return self.response({})

    @classmethod
    def urls(cls):
        """
        Urls that can be overridden in child classes
        :return:
        """
        return [
            url(r'^$', cls.as_view(handlers_dict={'get': 'get__list', 'post': 'post__list'}), name='list'),
            url(r'^(?P<pk>[0-9]*)/$', cls.as_view(handlers_dict={
                'get': 'get__object',
                'delete': 'delete__object',
                'post': 'post__object'}),
                name='object'),
        ]


from urllib.parse import urlencode

from .forms import LimitOffsetForm
from .settings import XREST_DEFAULT_LIST_LIMIT


class LimitOffsetPaginator(object):
    def __init__(self, request, queryset):
        self.errors = {}
        form = LimitOffsetForm(request.GET)
        if not form.is_valid():
            self.errors = form.errors

        self.offset = form.cleaned_data['offset'] or 0
        self.limit = form.cleaned_data['offset'] or XREST_DEFAULT_LIST_LIMIT
        self.queryset = queryset
        self.sliced_queryset = queryset
        self.request = request

    def get_queryset(self):
        return self.queryset

    def slice_queryset(self, queryset):
        sliced = self.get_queryset()[self.offset:self.offset+self.limit]
        self.sliced_queryset = sliced
        return sliced

    def build_next_url(self, offset):
        dct = self.request.GET.dict()
        dct['offset'] = offset
        dct['limit'] = self.limit
        return self.build_url(self.request, dct)

    def build_url(self, request, params):
        return '{url}?{params}'.format(url=request.path, params=urlencode(params))

    def build_previous_url(self, offset):
        dct = self.request.GET.dict()
        dct['offset'] = offset
        dct['limit'] = self.limit
        return self.build_url(self.request, dct)

    def meta(self):
        queryset = self.get_queryset()
        sliced_queryset = self.slice_queryset(queryset)
        overall_count = queryset.count()

        if overall_count > self.offset+self.limit:
            next_url = self.build_next_url(self.offset+self.limit)
        else:
            next_url = None

        if self.offset > 0:
            prev_offset = self.offset - self.limit
            if prev_offset < 0:
                prev_offset = 0
            prev_url = self.build_next_url(prev_offset)
        else:
            prev_url = None

        return {
            'count': sliced_queryset.count(),
            'overall_count': overall_count,
            'next_url': next_url,
            'previous_url': prev_url,
            'offset': self.offset,
            'limit': self.limit
        }
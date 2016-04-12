from django.conf import settings


def get_value(name, default_value):
    return getattr(settings, name, default_value)

# default limit in limit-offset paginator
XREST_DEFAULT_LIST_LIMIT = get_value('XREST_DEFAULT_LIST_LIMIT', 10)

# user for basic authorization backend
XREST_BASIC_AUTH_USER = get_value('XREST_BASIC_AUTH_USER', 'test')

# password for basic authorization backend
XREST_BASIC_AUTH_PASSWORD = get_value('XREST_BASIC_AUTH_PASSWORD', 'test')

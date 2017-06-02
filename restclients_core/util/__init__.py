try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode


def url_with_query(base, params):
    """
    Takes in a base url and a group of parameters/query, and returns a
    formatted url. Will be consistent between python 2 and 3.
    """
    return base + "?%s" % urlencode(params)

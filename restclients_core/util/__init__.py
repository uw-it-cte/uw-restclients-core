try:
    from urllib import quote_plus
    from urllib import urlencode as urllib_encode
except ImportError:
    from urllib.parse import urlencode as urllib_encode
    from urllib.parse import quote_plus


def format_url(base, params):
    """
    This is a utility method used to ensure that the query params are sorted
    consistently between python2 and python3.
    """
    return base + "?%s" % urlencode(params)


def urlencode(query, doseq=True, safe='', encoding=None, errors=None,
              quote_via=quote_plus):
    """
    This is a utility method used to ensure that the query params are sorted
    consistently between python2 and python3 by urlencode.
    """
    if type(query) is dict:
        query = [(key, query[key]) for key in sorted(query.keys())]
    elif type(query) is list and not all(query[i] <= query[i + 1]
                                         for i in range(len(query) - 1)):
        query = sorted(query, key=lambda tup: tup[0])

    return urllib_encode(query, doseq, safe, encoding, errors, quote_via)

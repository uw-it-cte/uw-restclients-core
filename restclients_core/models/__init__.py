from restclients_core.models.fields import (BooleanField, CharField, DateField,
                                            DateTimeField, DecimalField,
                                            FloatField, ForeignKey,
                                            IntegerField, NullBooleanField,
                                            PositiveIntegerField,
                                            PositiveSmallIntegerField,
                                            SlugField, SmallIntegerField,
                                            TextField, TimeField, URLField)


class MockHTTP(object):
    """
    An alternate object to HTTPResponse, for non-HTTP DAO
    implementations to use.  Implements the API of HTTPResponse
    as needed.
    """
    status = 0
    data = ""
    headers = {}

    def read(self):
        """
        Returns the document body of the request.
        """
        return self.data

    def getheader(self, field, default=''):
        """
        Returns the HTTP response header field, case insensitively
        """
        if self.headers:
            for header in self.headers:
                if field.lower() == header.lower():
                    return self.headers[header]

        return default


class Model(object):
    _dynamic_fields = []

    def __init__(self, *args, **kwargs):
        self._dynamic_fields = []

        super(Model, self).__init__()

        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __del__(self):
        # Fields are stored in a per-object-id dictionary.  Those ids are
        # guaranteed to be unique - but only over the lifetime of the object.
        # This makes sure those values are removed when this object
        # is destroyed.
        for field in self._dynamic_fields:
            field.__delete__(self)

    def clean_fields(self):
        for field in self._dynamic_fields:
            field.clean(self)

        pass

PROTECT = None

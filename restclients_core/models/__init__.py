from restclients_core.models.fields import (BooleanField, CharField, DateField,
                                            DateTimeField, DecimalField,
                                            FloatField,
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
    pass
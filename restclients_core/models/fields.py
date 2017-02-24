class BaseField(object):
    def __init__(self, *args, **kwargs):
        self._value = None
        super(BaseField, self).__init__()

    def __get__(self, instance, owner):
        return self._value

    def __set__(self, instance, value):
        self._value = value

    def __delete__(self, instance):
        self._value = None


class CharField(BaseField):
    pass


class BooleanField(BaseField):
    pass


class DateField(BaseField):
    pass


class DateTimeField(BaseField):
    pass


class DecimalField(BaseField):
    pass


class FloatField(BaseField):
    pass


class IntegerField(BaseField):
    pass


class NullBooleanField(BaseField):
    pass


class PositiveIntegerField(BaseField):
    pass


class PositiveSmallIntegerField(BaseField):
    pass


class SlugField(BaseField):
    pass


class SmallIntegerField(BaseField):
    pass


class TextField(BaseField):
    pass


class TimeField(BaseField):
    pass


class URLField(BaseField):
    pass

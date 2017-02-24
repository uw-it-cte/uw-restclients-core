class BaseField(object):

    def __init__(self, *args, **kwargs):
        self.values = {}
        self.dynamics = set()
        super(BaseField, self).__init__()

    def __get__(self, instance, owner):
        key = self._key_for_instance(instance)
        return self.values.get(key, None)

    def __set__(self, instance, value):
        key = self._key_for_instance(instance)

        if key not in self.dynamics:
            instance._dynamic_fields.append(self)
            self.dynamics.add(key)
        self.values[key] = value

    def __delete__(self, instance):
        key = self._key_for_instance(instance)
        if key in self.dynamics:
            self.dynamics.remove(key)
        del self.values[key]

    def _key_for_instance(self, instance):
        return id(instance)

    def clean(self, instance):
        pass


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


class ForeignKey(BaseField):
    pass

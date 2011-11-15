import abc
import collections
import copy


class DField(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def contribute_to_class(self, name, klass):
        pass

    @classmethod
    def __subclasshook__(cls, other):
        if cls is DField:
            if any("contribute_to_class" in base.__dict__ for base in other.__mro__):
                return True
        return NotImplemented

    def clone(self):
        return copy.copy(self)  

class DMeta(type):

    @classmethod
    def __prepare__(mcls, name, bases):
        return collections.OrderedDict()

    def __new__(mcls, name, bases, body):
        fields = []
        # Wyciągnij definicję
        for name, field in body.items():
            if not isinstance(field, DField):
                continue
            body.pop(name) # opcjonalne
            fields.append((name, field))

        cls = super().__new__(mcls, name, bases, body)

        # Zsumuj definicję
        base_fields = []
        for base in bases:
            base_fields.extend(base._fields.items())
        cls._fields = collections.OrderedDict(base_fields + fields)

        for name, field in cls._fields.items():
            field.contribute_to_class(name, cls)
        return cls


class ExtMeta(DMeta):

    @classmethod
    def __prepare__(mcls, name, bases):
        d = super().__prepare__(name, bases)
        for base in bases:
            for name, field in base._fields.items():
                d[name] = field.clone()
        return d


class Options(object):

    def __init__(self, *base_options):
        self.unique_tuples = []
        for base in base_options:
            self.unique_tuples.extend(base.unique_tuples)

    def add_unique(self, *fields):
        self.unique_tuples.append(fields)

class OptsMeta(ExtMeta):

    @classmethod
    def __prepare__(mcls, name, bases, **kwargs):
        d = super().__prepare__(name, bases)
        d["Meta"] = Options(*[base._options for base in bases])
        return d

    def __new__(mcls, name, bases, body, **kwargs):
        options = body.pop("Meta")
        cls = super().__new__(mcls, name, bases, body)
        cls._options = options
        return cls

    def __init__(cls, name, bases, body, abstract=False):
        cls.abstract = abstract

class Field:
    
    def contribute_to_class(self, name, cls):
        pass

    def clone(self):
        return copy.copy(self)  


class Base(metaclass=OptsMeta):
    pass

class A(Base, abstract=True):
    a = Field()

class B(A):
    b = Field()

    Meta.add_unique(a, b)

print(A.__dict__)
print(B.__dict__)

# Declarative Metaclass Pattern

----

# +Łukasz Rekucki

----

# What the hell are you talking about ?

----

# Django Forms


<div class="mcode">
    
    !python
    class UserCreationForm(forms.ModelForm):
        """
        A form that creates a user, with no privileges, 
        from the given username and password.
        """
        username = forms.RegexField(
                                label=_("Username"), 
                                max_length=30, 
                                regex=r'^[\w.@+-]+$')
                                
        password1 = forms.CharField(
                                label=_("Password"), 
                                widget=forms.PasswordInput)
                                
        password2 = forms.CharField(
                                label=_("Password confirmation"), 
                                widget=forms.PasswordInput)
    
        
        class Meta: # Meta, WTF ?
            model = User
            fields = ("username",)
</div>

----

# Django Models

<div class="scode">

    !python
    class Comment(BaseCommentAbstractModel):
        """
        A user comment about some object.
        """
        user        = models.ForeignKey(User, verbose_name=_('user'),
                        blank=True, null=True, 
                        related_name="%(class)s_comments")
                        
        user_name   = models.CharField(_("user's name"), 
                        max_length=50, blank=True)
        user_email  = models.EmailField(_("user's email address"), 
                        blank=True)
        user_url    = models.URLField(_("user's URL"), blank=True)
    
        comment = models.TextField(_('comment'), 
                        max_length=COMMENT_MAX_LENGTH)
    
        # Metadata about the comment
        submit_date = models.DateTimeField(_('date/time submitted'), 
                        default=None)
        ip_address  = models.IPAddressField(_('IP address'),
                        blank=True, null=True)

</div>

----

# Django Filters (by Alex Gaynor)

    !python
    class ProductFilter(django_filters.FilterSet):
    
        price = django_filters.NumberFilter(
                    lookup_type='lt')
            
        class Meta:
            model = Product
            fields = ['price', 'release_date']

----

# SQLAlchemy


<div class="mcode">

    !python
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()
    
    class Person(Base):
        __tablename__ = 'people'
        
        id = Column(Integer, primary_key=True)
        discriminator = Column('type', String(50))
        __mapper_args__ = {'polymorphic_on': discriminator}
    
    class Engineer(Person):
        __tablename__ = 'engineers'
        __mapper_args__ = {'polymorphic_identity': 'engineer'}
        
        id = Column(Integer, ForeignKey('people.id'), 
            primary_key=True)
        primary_language = Column(String(50))

</div>

----

# PyStruct

    !python
    @inpacket(0x01)
    class WelcomePacket(GaduPacket):
        seed = numeric.IntField(0)
    
    @inpacket(0x05)
    class MessageAckPacket(GaduPacket): #SendMsgAck
        MSG_STATUS = Enum({
            'BLOCKED': 0x0001, 'DELIVERED': 0x0002,
            'QUEUED': 0x0003, 'MBOXFULL': 0x0004,
            'NOT_DELIVERED': 0x0006
        })
    
        msg_status  = numeric.IntField(0)
        recipient   = numeric.IntField(1)
        seq         = numeric.IntField(2)
        
----

# Cechy wspólne

  * Klasa zawiera definicję "pól" w swojej treści. Opis danych, zamiast
    opisu zachowania.
  * Nie budujemy formularza. Podajemy tylko jakie właściwości ma on mieć.
  * Kolejność definicji ma znaczenie. Kolumny w tabeli zostaną utworzone
    w podanej kolejności. Tak samo ze struktrami w ``PyStruct``.
  * Nazwy specjalne: ``__tablename__``, `class Meta``, które są 
    tylko w definicji.
 
----

# Jak to działa ?

----

# Definicja klasy 

----

## Składnia

.fx: partial_start

    !python

    # Python 2
    class A(object):
        x = 10

    # Python 3
    class A:
        x = 10

    # Co się właściwie stanie ?

----

## Rozwinięcie

.fx: partial

    !python
    name = "A"
    bases = (object,)

    def _A():
      x = 10

    # Python 2
    body = {}

    # Python 3
    body = type.__prepare__(name, bases) 

    # i dalej:
    exec(_A.__code__, body, globals())
    A = type(name, bases, body)

----

# Dlaczego ``type`` ?

----

# Metaklasa

Formalnie jest to dowolny obiekt wywoływalny (ang. callable) przyjmujący 
wymienione trzy argumenty: ``name``, ``bases`` i ``body``.

(Py3k) Jeśli obiekt ma atrybut ``__prepare__``, to jest wywoływany
z argumentami ``name`` i ``bases`` do stworzenia ``body``.

    !python
    def meta(*args):
        print(args)
        return type(*args)

    # Python 2
    class B(A):
        __metaclass__ = meta

    # Python 3
    class B(A, metaclass=meta):
        pass

----

# Wybór metaklasy

Metaklasa jest wybierana na podstawie prostego
algorytmu:

<div class="mcode">

    !python
    if meta:
       isclass = issubclass(meta, type)
    else:
       if not bases:
           meta = type
       else:
           meta = bases[0].__class__
       isclass = True

    if isclass:
        for base in bases:
            if issubclass(meta, base):
                continue
            if issubclass(base, meta):
                meta = base
                continue
            raise TypeError("Konflikt")
    return meta

</div>    

----

# Tworzenie instancji przez (meta)klasę

    !python
    A = meta(name, bases, body)
    
    # znów rozwijamy:
    A = meta.__call__(name, bases, body)
    
    # jeśli ``meta`` jest klasą
    A = meta.__new__(name, bases, body)
    if isinstance(A, meta):
        meta.__init__(A, name, bases, body)

Będziemy więc nadpisywać ``__new__`` albo ``__init__`` w zależności od potrzeb.

----

# Klasa dla pól

Potrzebujemy osobnej klasy bazowej dla pól (może być abstrakcyjna, 
patrz moduł ``abc``), aby móc rozróżnić je od zwykłych metod.

Musimy też rozwiązać jakoś problem *kolejności*, gdyż domyślnie nazwy
zdefiniowane w ciele klasy są wkładane do słownika.

<div class="scode">

    !python
    
    class BaseField(object):
        _creation_counter = 0
        
        def __new__(cls, *args, **kwargs):
            instance = super(BaseField, cls).__new__(cls, *args, **kwargs)
            instance._creation_counter = BaseField._creation_counter
            BaseField._creation_counter += 1

</div>

----

# Metaklasa (Python 2)

<div class="scode">

    !python
    class DMeta(type):
    
        def __new__(mcls, name, bases, body):
            # Wyciągnij definicję
            fields = []
            for name, field in body.iteritems():
                if not isinstance(field, BaseField):
                    continue
                body.pop(name) # opcjonalne
                field.name = name
                fields.append((name, field))
            fields.sort(key=lambda f: f[1]._creation_counter)
            
            cls = super(mcls, type).__new__(mcls, name, bases, body)
            
            # Zsumuj definicję
            base_fields = []
            for base in bases:
                base_fields.extend(base._fields)
            cls._fields = collections.OrderedDict(base_fields + fields)
            
            for f in cls._fields:
                f.contribute_to_class(cls, f)
            return cls
</div>

----

# Metaklasa (Python 3)

<div class="scode">

    !python
    class DMeta(type):
    
        def __prepare__(mcls, name, bases):
            return collections.OrderedDict()
    
        def __new__(mcls, name, bases, body):
            
            # Wyciągnij definicję
            for name, field in body.iteritems():
                if not isinstance(field, BaseField):
                    continue
                body.pop(name) # opcjonalne
                field.name = name
                fields.append(field)
            
            cls = super().__new__(mcls, name, bases, body)
            
            # Zsumuj definicję
            base_fields = []
            for base in bases:
                base_fields.extend(base._fields)
            cls._fields = collections.OrderedDict(base_fields + fields)
            
            for f in cls._fields:
                f.contribute_to_class(cls, f)
            return cls
</div>

----

# Klasa ``Meta``

    !python
    class Struct(metaclass=DMeta):
        one = Field()
        two = Field()
    
        class Meta:
            unique_together = [('one', 'two')]
    
    
Pozwala definiować dodatkowe własności nie związane z&nbsp;konkretnym
polem unikająć kolizji z nazwami pól, bez używania wszędzie `__` i
nie zaśmiecając klasy.

----

# Po co właściwie to wszystko ?

----

# Co można zrobić lepiej w Py3k ?

----

## Pola z nadklasy

<div class="mcode">

    !python
    # Formularze Django:
    
    class ArticleForm(forms.Form):
        title = forms.CharField()
        category = forms.CharField(max_length=1, 
                        choices=(("N", "News"), ("R", "Review"))

    # Teraz chcemy stworzyć specjalny formularz dla News, więc
    # musimy ograniczyć category
    
    # Nie zadziała:
    class NewsForm(ArticleForm):
        category.choices = ((1, "News"),)
        
    # Można tak, ale musimy powtórzyć 
    # wszystkie inne opcje
    class NewsForm(ArticleForm):
        category = forms.CharField(max_length=1, 
                        choices=(("N", "News"),))
        
</div>
      
----

## Pola z nadklasy

<div class="mcode">

    !python
    class ExtMeta(DMeta):
    
        def __prepare__(mcls, name, bases):
            
            for base in bases:
                for name, field in base._fields.iteritems():
                    d[name] = field.clone()
            return d
            
    class NewsForm(ArticleForm, metaclass=ExtMeta):
        category.choices = ((1, "News"),)
                   
</div>            

----

## Pozbyć się ``Meta``


<div class="mcode">

    !python
    class Options(object):
    
        def add_unique(self, *fields):
            self.unique_tuples.append(fields)
        
    class OptsMeta(ExtMeta):
       
        def __prepare__(mcls, name, bases):
            d = super().__prepare__(mcls, name, bases)
            d["Meta"] = Options(bases)
            return d
            
    class A(metaclass=OptsMeta):
        a = Field()
        
    class B(A):
        b = Field()
    
        Meta.add_unique(a, b)

</div>

----

# Pomysły ?
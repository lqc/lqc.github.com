# Dekorowanie

----

# w URLconf

Ponieważ metoda `as_view()` zwraca zwyczajną funkcję, można jej używać ze zwykłymi dekoratorami:

<br>

    !python
    from django.views.generic import TemplateView
    from django.contrib.auth.decorators import login_required

    url(r'^/protected/$', login_required(
            TemplateView.as_view(template_name="secret.html")))

<br>

Jest to najprostsze podejście, jednak po dekoracji dostajemy funkcję. Nie da 
się w ten sposób zintegrować funkcjonalności na stałe z klasą tak jak to 
było w przypadku mixinów.

----

# Dekorator na metodzie

Django ma ukryty <q>skarb</q>, który pozwala łatwo dekorować metody:

<br>

    !python
    from django.utils.decorators import method_decorator

    class ProtectedView(View):
        
        @method_decorator(login_required):
        def dispatch(self, request, *args, **kwargs):
            return super(ProtectedView, self).dispatch(request, *args, **kwargs)

<br>

*Note:* Dekoratory takie jak `csrf_except` działają poprzez ustawienie atrybutu na widoku, który jest później 
sprawdzany przez middleware. Aby dało się ich używać z `dispatch()`, klasa `View` kopiuję wszystkie atrybuty z tej
metody na funkcję zwracaną przez `as_view()`.

Można też dekorować inne metody tj. `get()`, `post()`, `put()` czy `delete()`, ale 
`csrf_exempt` nie będzie na nich działał (i dobrze!).

----

# Dekorator na klasie

Niestety ten kod nie znalazł się w Django 1.3, ale jest bardzo użyteczny (Python 2.6+):

    !python
    def view_decorator(fdec)
        def decorator(cls):
            original = cls.as_view.im_func
            
            @functools.wraps(original)
            def as_view(current, **initkwargs):
                return fdec(original(current, **initkwargs))

            cls.as_view = classmethod(as_view) 
            return cls
        return decorator

    # użycie:

    @view_decorator(login_required)
    class ProtectedView(TemplateView):
        pass

    # *UWAGA*: można sobie strzelić w stopę 

    ProtectedView = view_decorator(login_required)(TemplateView)


# Decorating

----

# In URLconf

Because the `as_view()` method produces an ordinary function, you can 
apply function decorators to the result:

<br>

    !python
    from django.views.generic import TemplateView
    from django.contrib.auth.decorators import login_required

    url(r'^/protected/$', login_required(
            TemplateView.as_view(template_name="secret.html")))

<br>

This is simple, but after decorating you're left with a function, 
so subclassing is not possible.

----

# Decorating methods

Django provides an easy way to create method decorators:

<br>

    !python
    from django.utils.decorators import method_decorator

    class ProtectedView(View):
        
        @method_decorator(login_required):
        def dispatch(self, request, *args, **kwargs):
            return super(ProtectedView, self).dispatch(request, *args, **kwargs)

<br>

*Note:* Any attributes on `dispatch()` will get copied 
to the function returned by `as_view()`, so that `csrf_exempt` decorator works correctly.

You can also decorate `get()`, `post()`, `put()` and `delete()` this way, but 
`csrf_exempt` won't work with those methods.

----

# Class decorators

This actually didn't make it to Django 1.3, but I think it's very 
useful (requires Python 2.6):

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

    # usage:

    @view_decorator(login_required)
    class ProtectedView(TemplateView):
        pass

    # but **DO NOT** do this:

    ProtectedView = view_decorator(login_required)(TemplateView)

----

# Decorators vs. Mixins

* Both provide a way to add functionality in a reusable way.
* Decorators can't be overriden or extended, so you shouldn't use them in generic views.
* Mixins are not a very widely used concept in Python world and requires knowledge about MRO (Method Resolution Order).
* Neither are class decorators (Python 2.6+)
* Mixins don't work with function-based views. If you're writing a reusable application, 
you want to provide a decorator too.

There are no strict rules when to use one over other. 

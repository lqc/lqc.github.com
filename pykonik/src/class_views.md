# Pony <q>Magic</q>

----

<dl class="view-definition">
<dt>view (n.):</dt>
<dd>
<del>Function</del> <ins>Callable</ins> that takes a <code>Request</code> together with 
arguments from URL resolver and returns a <code>Response</code>.
</dd>
</dl>

In Python, any object with a `__call__` attribute is a *Callable*, e.g: 

* a function
* a class
* instance of a class with `__call__` method

----

# Why OOP is good for us ?

* Inheritance is good for code reuse as it makes overriding and extending behaviour eaiser.

* Multiply inheritance and _mixins_ let you reuse even more code.

* **Rule #1:** every time you need to make a decisions &mdash; call a method on `self`.

* But don't make too many one-line methods. Try to be flexible.

----

# The `View` class aka `Bikeshed` 

* There are different ways to implement the base class. See: 
`http://code.djangoproject.com/wiki/ClassBasedViews`

* They all have pros and cons, but most differences are purely cosmetic. 
This made it the major topic for bikeshedding on django&ndash;developers (~200 posts). 

Finally, a concesus was reached:


    !python
    class View(object):

        @classmethod
        def as_view(cls, **initargs):
            def real_view(*args, **kwargs):
                instance = cls(**initargs)
                return cls.dispatch(*args, **kwargs)
            return real_view

    # urls.py
    url('^sample-view/$', View.as_view(), name="sample_view")

----

# Writing simple views


    !python
    class ArticleList(View):
        template_name = "article_list.html"
        
       def get(self, request, *args, **kwargs):
            self.article_list = self.get_queryset()
            return self.render_to_response(
                self.get_context_data(articles=self.article_list))

        def render_to_response(self, context):
            return render_to_response(self.get_template_names(),
                context, RequestContext(self.request))

        def get_queryset(self):
            return Article.objects.all()

        def get_template_names(self):
            return [self.template_name] if self.template_name is not None else []

        def get_context_data(self, **kwargs):
            return kwargs
        

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

----

# The `View` class aka `Bikeshed` 

* There are many ways to implement the base class. See the [Wiki](http://code.djangoproject.com/wiki/ClassBasedViews).

* They all have pros and cons, but most differences are purely cosmetic. 
This made it the major topic for bikeshedding on django&ndash;developers 
(~200 posts last year). 

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

# A simple example


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
    
    # urls.py
    url('^articles/$', ArticleList.as_view(template_name="alternative.html"))

----

# Using mixins

You can compose mixins to reuse common functionality:

    !python
    from django.views.generic.base import TemplateResponseMixin, View
    from django.views.generic.list import ListView, MultipleObjectMixin

    class ArticleList(TemplateResponseMixin, MultipleObjectMixin, View):
        model = Article 
        template_name = "articles/article_list.html" 

        def get(self, request, *args, **kwargs):
            self.object_list = self.get_queryset()
            context = self.get_context_data(object_list=self.object_list)
            return self.render_to_response(context)

    
    class ArticleListTwo(ListView):
        model = Article 

You can also use mixins to override functionality:

    !python
    class JSONArticles(JSONMixin, ArticleList):
        pass

----

# More generic views

All function-based views have been migrated to <abbr title="Class-based Views">CBVs</abbr>.

  * `direct_to_template` &rarr; `TemplateView`
  * `redirect_to` &rarr; `RedirectView`
  * `object_list` &rarr; `ListView`
  * `object_detail` &rarr; `DetailView` 
  * `create_object` &rarr; `CreateView`  
  * `archive_year` &rarr; `YearArchiveView`
  * etc.

Together with some useful mixins, e.g:

  * `FormMixin` - form validation methods
  * `ModelFormMixin` - extends `FormMixin` to work with ModelForms.


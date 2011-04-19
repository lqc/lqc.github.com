# Pony <q>Magic</q>

----

<dl class="view-definition">
<dt>view (n.):</dt>
<dd>
<del>Funkcja</del> <ins>Obiekt typu <code>Callable</code></ins>, który bierze jako argument <code>WSGIRequest</code> oraz parametry 
dopasowane do ścieżki URL i zwraca <code>HTTPResponse</code>.
</dd>
</dl>

W Pythonie, dowolny obiekt może być wywoływalny, np.:

* funkcja
* klasa
* instancje klas z metodą `__call__`

----

----

# Krótka historia klasy `View`

* Istnieje wiele różnorodnych podejść do problemu. Większość opisana na [wiki](http://code.djangoproject.com/wiki/ClassBasedViews).

    * `__call__()` and `copy()` (bad!)
    * `__new__()` (good!)
    * `classmethod`
    * `classmethod2` (winner!)

* Każde ma swoje wady i zalety. Jednak większość różnic jest czysto kosmetyczna &rarr; Ponad 200 wiadomości na django&ndash;developers na ten temat. Nie wszystkie bardzo wartościowe.

----

# Klasa `View`


    !python
    class View(object):

        @classonlymethod
        def as_view(cls, **initargs):
            def view(*args, **kwargs):
                self = cls(**initargs)
                return self.dispatch(*args, **kwargs)
            update_wrapper(view, cls, updated=())
            update_wrapper(view, cls.dispatch, assigned=())
            return view

        def dispatch(self, request, *args, **kwargs):
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(), 
                    self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            self.request = request
            self.args = args
            self.kwargs = kwargs
            return handler(request, *args, **kwargs)

    # urls.py
    url('^sample-view/$', View.as_view(), name="sample_view")

----

# Prosty przykład


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

# Mixins

Wielodziedziczenie pomaga w ponownym wykorzystaniu kodu:

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

Można też nadpisać funkcjonalność, a nie tylko rozszerzać:

    !python
    class JSONArticles(JSONMixin, ArticleList):
        pass

----

# Więcej generycznych widoków

Wszystkie dotychczasowe generyczne widoki zostały zmigrowane do <abbr title="Class-based Views">CBV</abbr>.

  * `direct_to_template` &rarr; `TemplateView`
  * `redirect_to` &rarr; `RedirectView`
  * `object_list` &rarr; `ListView`
  * `object_detail` &rarr; `DetailView` 
  * `create_object` &rarr; `CreateView`  
  * `archive_year` &rarr; `YearArchiveView`
  * etc.

Są one posklejane z mixinów takich jak:

  * `FormMixin` - walidacja formularzy, przetwarzanie GET/POST
  * `ModelFormMixin` - j.w. ale działa z ModelForms.

----

# Przykład przetwarzania formularza

    !python
    from django.views.generic import CreateView
    from myapp.signals import custom_signal

    class CreateArticleView(CreateView):

        def get_form_kwargs(self):
            kwargs = super(CreateArticleView, self).get_form_kwargs()
            # domyślnie: 'data', 'files' i 'initial'
            kwargs['author'] = self.request.user
            return kwargs

        def form_valid(self, form):
            """Called when the form is valid"""
            response = super(CreateArticleView, self).form_valid(form)
            if self.object:
                custom_signal.send(sender=type(self.object), instance=self.object)
            # dodaj `message`, dodaj zadanie do Celery, itp.
            return response

----


# Para niecnych tricków


    !python
    class DelayedModelFormMixin(ModelFormMixin):

        def form_valid(self, form):
            self.object = form.save(commit=False)
            self.prepare_object_for_save(self.object)
            self.object.save()
            self.object.save_m2m()
            # wyślij sygnał...
            return super(ModelFormMixin, self).form_valid(form)

        def prepare_object_for_save(self, obj):
            pass

    class CreateCommentView(DelayedModelFormMixin, CreateView):

        def prepare_object_for_save(self, obj)
            obj.author = self.request.user


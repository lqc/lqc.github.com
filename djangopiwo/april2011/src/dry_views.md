# Czym jest widok ?

----

<dl class="view-definition">
<dt>view (n.):</dt>
<dd>
Funkcja, która bierze jako argument <code>WSGIRequest</code> oraz parametry 
dopasowane do ścieżki URL i zwraca <code>HTTPResponse</code>.
</dd>
</dl>


    !python
    def article_list(request):
        articles = Article.objects.all()
        return render_to_response("article_list.html", {"articles": articles}, 
                   context_instance=RequestContext(request))

.notes: Talk about how to extend this view to be more reusable

----

# Be DRY!

----

.fx: largelisting listing50 

    !python
    def object_list(request, queryset, paginate_by=None, page=None,
            allow_empty=True, template_name=None, template_loader=loader,
            extra_context=None, context_processors=None, template_object_name='object',
            mimetype=None):
        if extra_context is None: extra_context = {}
        queryset = queryset._clone()
        if paginate_by:
            paginator = Paginator(queryset, paginate_by, allow_empty_first_page=allow_empty)
            if not page:
                page = request.GET.get('page', 1)
            try:
                page_number = int(page)
            except ValueError:
                if page == 'last':
                    page_number = paginator.num_pages
                else:
                    # Page is not 'last', nor can it be converted to an int.
                    raise Http404
            try:
                page_obj = paginator.page(page_number)
            except InvalidPage:
                raise Http404
            c = RequestContext(request, {
                '%s_list' % template_object_name: page_obj.object_list,
                'paginator': paginator,
                'page_obj': page_obj,
                'is_paginated': page_obj.has_other_pages(),
            }, context_processors)
        else:
            c = RequestContext(request, {
                '%s_list' % template_object_name: queryset,
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
            }, context_processors)
            if not allow_empty and len(queryset) == 0:
                raise Http404
        for key, value in extra_context.items():
            if callable(value):
                c[key] = value()
            else:
                c[key] = value
        if not template_name:
            model = queryset.model
            template_name = "%s/%s_list.html" % (model._meta.app_label, model._meta.object_name.lower())
        t = template_loader.get_template(template_name)
        return HttpResponse(t.render(c), mimetype=mimetype)

.notes: Talk about how this view is incomplete: different Paginator, Jinja2 templates, GET field for page.

----

.fx: largelisting

    !python
    def twitter_login_done(request):
        request_token = request.session.get('request_token', None)
        verifier = request.GET.get('oauth_verifier', None)
        denied = request.GET.get('denied', None)
        # If we've been denied, put them back to the signin page
        # They probably meant to sign in with facebook >:D
        if denied:
            return HttpResponseRedirect(reverse("socialauth_login_page"))
        # If there is no request_token for session,
        # Means we didn't redirect user to twitter
        if not request_token:
            # Redirect the user to the login page,
            return HttpResponseRedirect(reverse("socialauth_login_page"))
        token = oauth.Token.from_string(request_token)
        # If the token from session and token from twitter does not match
        # means something bad happened to tokens
        if token.key != request.GET.get('oauth_token', 'no-token'):
            del_dict_key(request.session, 'request_token')
            # Redirect the user to the login page
            return HttpResponseRedirect(reverse("socialauth_login_page"))
        try:
            twitter = oauthtwitter.TwitterOAuthClient(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
            access_token = twitter.fetch_access_token(token, verifier)
            request.session['access_token'] = access_token.to_string()
            user = authenticate(twitter_access_token=access_token)
        except:
            user = None
        # if user is authenticated then login user
        if user:
            login(request, user)
        else:
            # We were not able to authenticate user
            # Redirect to login page
            del_dict_key(request.session, 'access_token')
            del_dict_key(request.session, 'request_token')
            return HttpResponseRedirect(reverse('socialauth_login_page'))
        # authentication was successful, use is now logged in
        next = request.session.get('twitter_login_next', None)
        if next:
            del_dict_key(request.session, 'twitter_login_next')
            return HttpResponseRedirect(next)
        else:
            return HttpResponseRedirect(LOGIN_REDIRECT_URL)


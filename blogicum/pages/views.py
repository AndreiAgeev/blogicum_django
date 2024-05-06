from django.shortcuts import render, redirect
from django.views.generic import TemplateView


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def access_denied(request, exception):
    # string = request.get_full_path().split('/')[0:-2]
    # string = '/'.join(string) + '/'
    # string = request.build_absolute_uri().split('/')[0:-2]
    # string = '/'.join(string) + '/'
    # return redirect(string)
    return render(request, 'pages/403csrf.html', status=403)


def server_internal_error(request):
    return render(request, 'pages/500.html', status=500)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)

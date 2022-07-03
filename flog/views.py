from datetime import date, datetime, timedelta
#import logging

from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from tagging.models import *

from flog.models import Day, Entry, Swallow
from flog.forms import EntryForm


#if sys.version >= '2.4':
#    logging.basicConfig(
#        level=logging.WARNING,
#        format=settings.DEBUG_LOG_FORMAT,
#        datefmt=settings.DEBUG_LOG_DATEFMT,)
#else:
#    logging.basicConfig()


def app_context(request):
    """Context processor that handles variables used in many views.
    """
    domain = Site.objects.get_current().domain
    app_path = '/flog'
    return {
        'app_path': app_path,
        'domain': domain,
    }

# views -----------------------------------------------------------------------

@login_required
def index(request):
    """Default page of the flog.
    """
    redirect = '/flog/%s/' % date.today().strftime('%Y/%m/%d')
    if request.GET.get('mobile', None):
        entries = None
        swallows = None
        template = 'flog/index-mobile.html'
        redirect = '%s?mobile=1' % redirect
    else:
        entries = Entry.objects.all()[:50]
        swallows = Swallow.objects.all()[:50]
        template='flog/index.html'
    # form
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            e = Entry()
            e.txt = form.cleaned_data['txt']
            e.save()
            return HttpResponseRedirect(redirect)
    else:
        form = EntryForm()
    return render_to_response(template,
        {
        'request': request,
        'entries': entries,
        'swallows': swallows,
        'form': form,
        },
        context_instance=RequestContext(request, processors=[app_context])
    )

@login_required
def day(request, yyyy, mm, dd):
    """
    """
    if request.GET.get('mobile', None):
        template = 'flog/day-mobile.html'
    else:
        template='flog/day.html'
    tday = date(int(yyyy), int(mm), int(dd))
    day = Day.objects.get(date=tday)
    sod = datetime(tday.year,tday.month,tday.day, 0,0,0)
    eod = datetime(tday.year,tday.month,tday.day, 23,59,59)
    day.get_sparkline_data()
    return render_to_response(template,
        {
        'request': request,
        'today': tday,
        'yesterday': tday - timedelta(1),
        'tomorrow': tday + timedelta(1),
        'day': day,
        'entries': Entry.objects.filter(created__gte=sod, created__lte=eod),
        'swallows': Swallow.objects.filter(created__gte=sod, created__lte=eod),
        },
        context_instance=RequestContext(request, processors=[app_context])
    )

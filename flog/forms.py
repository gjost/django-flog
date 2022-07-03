from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import widgets             
from django.db import models
from django.forms.util import ErrorList

from tagging.forms import TagField

from flog.models import Swallow, ENTRY_HELP_TEXT


class EntryForm(forms.Form):
    """Flog entry form
    """
    txt = forms.CharField(help_text=ENTRY_HELP_TEXT)

from django.contrib import admin
from flog.models import Day, Entry, Swallow


class DayAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': (
            'date', 
            'incomplete', 
            ('weight', 'weight_empty',), 
            'calories',
            'hours_slept', 
            ('coffee_cups', 'coffee_oz',),
            'p1', 
        )}),
    )
    list_display = [
        'date', 'incomplete', 'weight', 'calories', 'coffee_cups', 'p1',]
    list_display_links = ['date',]
    ordering = ['-date',]
    list_filter = ['date',]

class EntryAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': (
            'txt',
            'created', 
        )}),
    )
    list_display = ['created', 'txt',]
    list_display_links = ['created',]
    ordering = ['-created',]
    list_filter = ['created',]
    search_fields = [
        'txt', 
    ]

class SwallowAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': (
            'title', 
            'tags', 
            'serving_size', 
            'calories', 
            'description', 
            'created', 
        )}),
    )
    list_display = ['created', 'title', 'serving_size', 'calories', 'tags',]
    list_display_links = ['created',]
    ordering = ['-created',]
    list_filter = ['created',]
    search_fields = [
            'title', 
            'description', 
            'tags', 
    ]

admin.site.register(Day, DayAdmin)
admin.site.register(Entry, EntryAdmin)
admin.site.register(Swallow, SwallowAdmin)

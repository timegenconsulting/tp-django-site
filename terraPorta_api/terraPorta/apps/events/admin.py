from django.contrib import admin

from terraPorta.apps.events.models import Events, EventHook, EventService

admin.site.register(EventService)
admin.site.register(Events)


@admin.register(EventHook)
class EventHookAdmin(admin.ModelAdmin):
    list_display = ['id', 'event', 'org', 'user', 'hook_link']

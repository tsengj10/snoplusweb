from django.contrib import admin

from .models import Resource, Approver, Booking, Zone, Comment

# Register your models here.

class BookingAdmin(admin.ModelAdmin):
  readonly_fields = ( 'request_time', 'modification_time', )
  fields = ( 'user', 'group', 'resource',
             'begin_time', 'end_time',
             'request_time', 'modification_time',
             'user_note', 'approver_note',
             'approval',
           )

admin.site.register(Zone)
admin.site.register(Resource)
admin.site.register(Approver)
admin.site.register(Comment)
admin.site.register(Booking, BookingAdmin)


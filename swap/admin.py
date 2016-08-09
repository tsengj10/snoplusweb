from django.contrib import admin

from .models import Resource, Booking, Zone

# Register your models here.

class BookingAdmin(admin.ModelAdmin):
  readonly_fields = ( 'request_time', 'modification_time', )
  fields = ( 'user', 'booker', 'charge_group', 'resource',
             'begin_time', 'end_time',
             'request_time', 'modification_time',
           )

admin.site.register(Zone)
admin.site.register(Resource)
admin.site.register(Booking, BookingAdmin)


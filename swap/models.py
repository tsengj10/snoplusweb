from django.db import models

# Create your models here.

class Resource(models.Model):
  # a resource to be swapped
  name = models.CharField(max_length=100)
  description = models.TextField(blank=True)
  default_begin_time = models.TimeField()
  default_end_time = models.TimeField()
  group = models.ForeignKey('auth.Group')

  def __str__(self):
    return self.name

class Approver(models.Model):
  # a mapping between persons who can approve use of a resource, and the resource
  user = models.ForeignKey('auth.User')
  resource = models.ForeignKey('Resource', related_name='approver')

  def __str__(self):
    return "{0} ({1})".format(self.user, self.resource)

class Booking(models.Model):
  # a booking of a resource by a person
  user = models.ForeignKey('auth.User')
  group = models.ForeignKey('auth.Group', help_text='group to charge')
  resource = models.ForeignKey('Resource', related_name='booking')
  approval = models.ForeignKey('Approver', related_name='approval',
                               null=True, default=None,
                               help_text="booking approved by whom")
  user_note = models.TextField(blank=True)
  approver_note = models.TextField(blank=True)
  begin_time = models.DateTimeField()
  end_time = models.DateTimeField()
  request_time = models.DateTimeField(auto_now_add=True)
  modification_time = models.DateTimeField(auto_now=True)

  def __str__(self):
    return "{0} {1} ({2})".format(self.begin_time, self.user, self.resource)


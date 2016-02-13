from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, User
from django.conf import settings
import json

from swap.models import *

class Command(BaseCommand):
  help = 'Generate configuration json'

  def add_arguments(self, parser):
    parser.add_argument('filename', nargs='?', default='swap/static/json/config.json')

  def handle(self, *args, **options):
    filename = options['filename']

    d = {
          "tzs": [ settings.TIME_ZONE ],
          "res": [],
          "us": [],
          "gs": [],
          "aps": [],
        }
    for n in Zone.objects.all():
      if n.name not in d["tzs"]:
        d["tzs"].append(n.name)
    for g in Group.objects.all().order_by('name'):
      d["gs"].append({ "pk": g.pk, "name": g.name, "u": [], "r": [] })
    for r in Resource.objects.all().order_by('name'):
      d["res"].append({ "pk": r.pk, "name": r.name,
                        "dbt": r.default_begin_time.isoformat(),
                        "det": r.default_end_time.isoformat(),
                        "dz" : r.default_zone.name })
      for gs in d["gs"]:
        if r.group.pk == gs["pk"]:
          gs["r"].append(r.pk)
          break
    for u in User.objects.all().order_by('username'):
      gs = u.groups.first()
      d["us"].append({ "pk": u.pk, "name": u.username, "g": gs.pk })
      for g in u.groups.all():
        for gs in d["gs"]:
          if g.pk == gs["pk"]:
            gs["u"].append(u.pk)
            break
    for a in Approver.objects.all():
      d["aps"].append({ "u": a.user.pk, "r": a.resource.pk })

    f = open(filename, 'w')
    data = { "data": d }
    json.dump(data, f)
    f.close()

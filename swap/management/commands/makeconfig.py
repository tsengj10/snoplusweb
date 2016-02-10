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
    for r in Resource.objects.all():
      d["res"].append({ "pk": r.pk, "name": r.name,
                        "dbt": r.default_begin_time.isoformat(),
                        "det": r.default_end_time.isoformat(),
                        "dz" : r.default_zone.name })
    for u in User.objects.all():
      gs = u.groups.first()
      d["us"].append({ "pk": u.pk, "name": u.username, "g": gs.name })
    for g in Group.objects.all():
      d["gs"].append({ "pk": g.pk, "name": g.name })
    for a in Approver.objects.all():
      d["aps"].append({ "u": a.user.pk, "r": a.resource.pk })

    f = open(filename, 'w')
    data = { "data": d }
    json.dump(data, f)
    f.close()

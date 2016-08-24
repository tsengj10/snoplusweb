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
          "tzs": [],
          "gs": [],
          "us": [],
          "res": [],
        }

    for n in Zone.objects.all():
      if n.name not in d["tzs"]:
        d["tzs"].append(n.name)

    for g in Group.objects.all().order_by('name'):
      d["gs"].append({ "pk": g.pk, "name": g.name, "u": [], "ru": [], "ra": [] })

    for r in Resource.objects.all().order_by('name'):
      d["res"].append({ "pk": r.pk, "name": r.name,
                        "desc": r.description,
                        "dbt": r.default_begin_time.isoformat(),
                        "det": r.default_end_time.isoformat(),
                        "dz" : r.default_zone.name,
                        "adv": r.advance_period,
                        "ot": r.open_time,
                        "ct": r.close_time,
                        "mt": r.modification_time.isoformat() })
      for gs in d["gs"]:
        if r.user_group.pk == gs["pk"]:
          gs["ru"].append(r.pk)
        if r.admin_group.pk == gs["pk"]:
          gs["ra"].append(r.pk)

    for u in User.objects.all().order_by('last_name', 'first_name'):
      d["us"].append({ "pk": u.pk, "name": u.username,
                       "n1": u.first_name, "n2": u.last_name })
      for g in u.groups.all():
        for gs in d["gs"]:
          if g.pk == gs["pk"]:
            gs["u"].append(u.pk)
            break

    f = open(filename, 'w')
    data = { "data": d }
    json.dump(data, f)
    f.close()

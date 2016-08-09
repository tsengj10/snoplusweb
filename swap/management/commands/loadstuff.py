from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group, User
from django.conf import settings
import json

from swap.models import *

class Command(BaseCommand):
  help = 'Load resource, user, and group information'

  def add_arguments(self, parser):
    parser.add_argument('filename', nargs='?',
                        default='swap/fixtures/testdata.json')

  def handle(self, *args, **options):
    filename = options['filename']

    with open(filename) as json_file:
      d = json.load(json_file)

    for z in d["zones"]:
      obj, created = Zone.objects.update_or_create(name=z["name"]);

    for g in d["groups"]:
      obj, created = Group.objects.update_or_create(name=g["name"])
      print("Group {} {}".format(obj, "created" if created else "updated"))

    for u in d["users"]:
      obj, created = User.objects.update_or_create(username=u["username"], defaults=u["data"])
      print("User {} {}".format(obj, "created" if created else "updated"))
      try:
        obj.groups = [ Group.objects.get(name=n) for n in u["groups"] ]
      except ObjectDoesNotExist:
        print("Invalid groups for user {}".format(u["username"]))

    for r in d["resources"]:
      try:
        r["data"]["user_group"] = Group.objects.get(name=r["group"])
        r["data"]["admin_group"] = Group.objects.get(name=r["admin"])
        r["data"]["default_zone"] = Zone.objects.get(name=r["zone"])
      except ObjectDoesNotExist:
        print("Invalid groups for resource {}".format(r["name"]))
      obj, created = Resource.objects.update_or_create(name=r["name"], defaults=r["data"])
      print("Resource {} {}".format(obj, "created" if created else "updated"))


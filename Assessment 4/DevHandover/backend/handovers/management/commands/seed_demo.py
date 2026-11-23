from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
class Command(BaseCommand):
 help='Create local-only demonstration accounts; do not run on production.'
 def handle(self,*args,**kwargs):
  User=get_user_model();group,_=Group.objects.get_or_create(name='handover_managers')
  for username,manager in [('manager',True),('outgoing',False),('incoming',False)]:
   user,created=User.objects.get_or_create(username=username)
   if created:user.set_password('DemoPass123!');user.save()
   if manager:user.groups.add(group)
   self.stdout.write(f'{username}: {"created" if created else "already exists"}')
  self.stdout.write('Development-only password for newly created accounts: DemoPass123!')

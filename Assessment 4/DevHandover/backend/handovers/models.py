from django.conf import settings
from django.db import models

TEMPLATE=(('repository','Repository access',True),('setup','Setup instructions',True),('architecture','Architecture overview',True),('deployment','Deployment guide',True),('issues','Known issues',False),('tasks','Outstanding tasks',False))
class Project(models.Model):
 name=models.CharField(max_length=120)
 description=models.TextField(max_length=2000)
 target_date=models.DateField()
 created_at=models.DateTimeField(auto_now_add=True)
 accepted_at=models.DateTimeField(null=True,blank=True)
 accepted_by=models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.PROTECT,related_name='accepted_handovers')
 @property
 def is_accepted(self): return self.accepted_at is not None
 def __str__(self): return self.name

class Membership(models.Model):
 class Role(models.TextChoices):
  MANAGER='manager','Project manager'
  OUTGOING='outgoing','Outgoing developer'
  REVIEWER='reviewer','Incoming reviewer'
  LEAD='lead','Incoming lead'
 project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='memberships')
 user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='handover_memberships')
 role=models.CharField(max_length=12,choices=Role.choices)
 class Meta:
  constraints=[models.UniqueConstraint(fields=['project','user','role'],name='one_member_role_per_project')]

class ChecklistItem(models.Model):
 class Status(models.TextChoices):
  DRAFT='draft','Draft'
  SUBMITTED='submitted','Ready for review'
  CHANGES='changes_requested','Changes requested'
  VERIFIED='verified','Verified'
 project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='items')
 category=models.CharField(max_length=30)
 title=models.CharField(max_length=120)
 is_critical=models.BooleanField(default=False)
 status=models.CharField(max_length=20,choices=Status.choices,default=Status.DRAFT)
 documentation_url=models.URLField(max_length=2048,blank=True)
 notes=models.TextField(blank=True)
 version=models.PositiveIntegerField(default=0)
 reviewed_by=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,null=True,blank=True,related_name='+')
 reviewed_at=models.DateTimeField(null=True,blank=True)
 review_comment=models.TextField(blank=True,max_length=2000)
 updated_at=models.DateTimeField(auto_now=True)
 class Meta:
  constraints=[models.UniqueConstraint(fields=['project','category'],name='one_category_per_project')]
 def __str__(self):return f'{self.project.name}: {self.title}'

class ActivityEntry(models.Model):
 project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='activity')
 item=models.ForeignKey(ChecklistItem,on_delete=models.CASCADE,null=True,blank=True)
 actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT)
 action=models.CharField(max_length=40)
 details=models.CharField(max_length=300,blank=True)
 created_at=models.DateTimeField(auto_now_add=True)
 class Meta:
  ordering=['-created_at','-id']

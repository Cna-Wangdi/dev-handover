from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Project,Membership,ChecklistItem,ActivityEntry
User=get_user_model()
class UserSerializer(serializers.ModelSerializer):
 class Meta: model=User;fields=['id','username','first_name','last_name']
class MemberSerializer(serializers.ModelSerializer):
 username=serializers.CharField(source='user.username',read_only=True)
 class Meta: model=Membership;fields=['id','user','username','role']
class ItemSerializer(serializers.ModelSerializer):
 reviewed_by_name=serializers.CharField(source='reviewed_by.username',read_only=True,default=None)
 class Meta:
  model=ChecklistItem
  fields=['id','category','title','is_critical','status','documentation_url','notes','version','reviewed_by_name','reviewed_at','review_comment','updated_at']
class ActivitySerializer(serializers.ModelSerializer):
 actor_name=serializers.CharField(source='actor.username',read_only=True)
 class Meta: model=ActivityEntry;fields=['id','item','actor_name','action','details','created_at']
class ProjectSerializer(serializers.ModelSerializer):
 memberships=MemberSerializer(many=True,read_only=True)
 items=ItemSerializer(many=True,read_only=True)
 activity=ActivitySerializer(many=True,read_only=True)
 progress=serializers.SerializerMethodField()
 critical_ready=serializers.SerializerMethodField()
 class Meta:
  model=Project;fields=['id','name','description','target_date','created_at','accepted_at','accepted_by','memberships','items','activity','progress','critical_ready']
 def get_progress(self,obj):
  if hasattr(obj,'items'):
   items=list(obj.items.all());return round(100*sum(x.status=='verified' for x in items)/len(items)) if items else 0
  return 0
 def get_critical_ready(self,obj):
  items=list(obj.items.all());critical=[x for x in items if x.is_critical]
  return {'verified':sum(x.status=='verified' for x in critical),'total':len(critical),'ready':bool(critical) and all(x.status=='verified' for x in critical)}
class ProjectCreateSerializer(serializers.Serializer):
 name=serializers.CharField(max_length=120,trim_whitespace=True)
 description=serializers.CharField(max_length=2000,trim_whitespace=True)
 target_date=serializers.DateField()
 outgoing=serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_active=True))
 incoming=serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_active=True))
 def validate(self,attrs):
  if attrs['outgoing']==attrs['incoming']:raise serializers.ValidationError({'incoming':'Outgoing and incoming users must differ to prevent self-verification.'})
  return attrs

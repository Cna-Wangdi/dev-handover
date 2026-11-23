from urllib.parse import urlsplit
from django.contrib.auth import authenticate,login,logout
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from .models import Project,Membership,ChecklistItem,ActivityEntry,TEMPLATE
from .serializers import UserSerializer,ProjectSerializer,ProjectCreateSerializer,ItemSerializer

def error(message,code=400):return Response({'detail':message},status=code)
def roles(user,project):return set(Membership.objects.filter(user=user,project=project).values_list('role',flat=True))
def member(user,project):return bool(roles(user,project))
def get_project(user,pk):
 p=Project.objects.filter(pk=pk).first()
 return p if p and member(user,p) else None
def valid_url(url):
 try:
  u=urlsplit(url)
  return u.scheme.lower() in ('http','https') and bool(u.hostname) and not u.username and not u.password
 except ValueError:return False

@ensure_csrf_cookie
def csrf(request):return JsonResponse({'csrfToken':get_token(request)})

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
def sign_in(request):
 username=request.data.get('username','');password=request.data.get('password','')
 user=authenticate(request,username=username,password=password)
 if user is None:return error('Invalid username or password.',401)
 login(request,user)
 return Response({'user':UserSerializer(user).data,'is_manager':user.groups.filter(name='handover_managers').exists()})

@api_view(['POST'])
def sign_out(request):
 logout(request)
 return Response({'detail':'Signed out.'})

@api_view(['GET'])
def me(request):return Response({'user':UserSerializer(request.user).data,'is_manager':request.user.groups.filter(name='handover_managers').exists()})

@api_view(['GET'])
def users(request):
 if not request.user.groups.filter(name='handover_managers').exists():return error('Manager permission required.',403)
 from django.contrib.auth import get_user_model
 return Response(UserSerializer(get_user_model().objects.filter(is_active=True).order_by('username'),many=True).data)

@api_view(['GET','POST'])
def projects(request):
 if request.method=='GET':
  qs=Project.objects.filter(memberships__user=request.user).distinct().order_by('-created_at')
  return Response(ProjectSerializer(qs,many=True).data)
 if not request.user.groups.filter(name='handover_managers').exists():return error('Manager permission required.',403)
 serializer=ProjectCreateSerializer(data=request.data)
 serializer.is_valid(raise_exception=True)
 d=serializer.validated_data
 with transaction.atomic():
  p=Project.objects.create(name=d['name'],description=d['description'],target_date=d['target_date'])
  Membership.objects.bulk_create([Membership(project=p,user=request.user,role='manager'),Membership(project=p,user=d['outgoing'],role='outgoing'),Membership(project=p,user=d['incoming'],role='lead')])
  ChecklistItem.objects.bulk_create([ChecklistItem(project=p,category=c,title=t,is_critical=k) for c,t,k in TEMPLATE])
  ActivityEntry.objects.create(project=p,actor=request.user,action='project_created',details='Six checklist items generated')
 return Response(ProjectSerializer(p).data,status=201)

@api_view(['GET'])
def project_detail(request,pk):
 p=get_project(request.user,pk)
 if not p:return error('Project not found.',404)
 return Response(ProjectSerializer(p).data)

@api_view(['POST'])
def evidence(request,pk,item_id):
 p=get_project(request.user,pk)
 if not p:return error('Project not found.',404)
 with transaction.atomic():
  p=Project.objects.select_for_update().get(pk=p.pk)
  item=ChecklistItem.objects.select_for_update().filter(pk=item_id,project=p).first()
  if not item:return error('Item not found.',404)
  if p.is_accepted:return error('Accepted handovers are read-only.',409)
  if 'outgoing' not in roles(request.user,p):return error('Outgoing developer permission required.',403)
  if item.status not in ('draft','changes_requested'):return error('Only Draft and Changes requested items are editable.',409)
  action=request.data.get('action')
  if action not in ('save','submit'):return error('Action must be save or submit.')
  if request.data.get('version')!=item.version:return error('This item changed. Reload before editing.',409)
  url=str(request.data.get('documentation_url','')).strip()
  notes=str(request.data.get('notes','')).strip()
  if len(url)>2048 or (url and not valid_url(url)):return error('Supply an absolute http/https URL (maximum 2048 characters), without embedded credentials.')
  if len(notes)>10000:return error('Notes must be at most 10000 characters.')
  if action=='submit' and (not url or not notes):return error('Submission requires a documentation URL and non-blank notes.')
  item.documentation_url=url;item.notes=notes
  if action=='submit':item.status='submitted'
  item.version+=1;item.save()
  ActivityEntry.objects.create(project=p,item=item,actor=request.user,action='submitted' if action=='submit' else 'draft_saved')
  return Response(ItemSerializer(item).data)

@api_view(['POST'])
def review(request,pk,item_id):
 p=get_project(request.user,pk)
 if not p:return error('Project not found.',404)
 with transaction.atomic():
  p=Project.objects.select_for_update().get(pk=p.pk)
  item=ChecklistItem.objects.select_for_update().filter(pk=item_id,project=p).first()
  if not item:return error('Item not found.',404)
  if p.is_accepted:return error('Accepted handovers are read-only.',409)
  if not roles(request.user,p).intersection({'lead','reviewer'}):return error('Incoming reviewer permission required.',403)
  if 'outgoing' in roles(request.user,p):return error('You cannot verify your own evidence.',403)
  if request.data.get('version')!=item.version:return error('This item changed. Reload before reviewing.',409)
  action=request.data.get('action');comment=str(request.data.get('comment','')).strip()
  if action=='verify' and item.status=='submitted':
   item.status='verified';item.review_comment=''
  elif action=='corrections' and item.status in ('submitted','verified'):
   if not comment or len(comment)>2000:return error('Correction comment must contain 1–2000 characters.')
   item.status='changes_requested';item.review_comment=comment
  else:return error('Review action not allowed in the current state.',409)
  item.reviewed_by=request.user;item.reviewed_at=timezone.now();item.version+=1;item.save()
  ActivityEntry.objects.create(project=p,item=item,actor=request.user,action='verified' if action=='verify' else 'corrections_requested',details=comment[:300])
  return Response(ItemSerializer(item).data)

@api_view(['POST'])
def accept(request,pk):
 p=get_project(request.user,pk)
 if not p:return error('Project not found.',404)
 with transaction.atomic():
  p=Project.objects.select_for_update().get(pk=p.pk)
  if p.is_accepted:return error('Handover already accepted.',409)
  if 'lead' not in roles(request.user,p):return error('Incoming lead permission required.',403)
  if request.data.get('confirm') is not True:return error('Explicit responsibility confirmation is required.')
  critical=list(ChecklistItem.objects.filter(project=p,is_critical=True))
  if not critical or any(x.status!='verified' for x in critical):return error('All Critical checklist items must be Verified.',409)
  p.accepted_by=request.user;p.accepted_at=timezone.now();p.save(update_fields=['accepted_by','accepted_at'])
  ActivityEntry.objects.create(project=p,actor=request.user,action='accepted',details='Responsibility confirmed')
  return Response(ProjectSerializer(p).data)

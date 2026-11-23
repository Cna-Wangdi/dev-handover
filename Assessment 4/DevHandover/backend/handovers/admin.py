from django.contrib import admin
from .models import Project,Membership,ChecklistItem,ActivityEntry
class ItemInline(admin.TabularInline):
 model=ChecklistItem;extra=0;readonly_fields=('category','title','is_critical','status');can_delete=False
class MembershipInline(admin.TabularInline):
 model=Membership;extra=0
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
 list_display=('name','target_date','accepted_at');inlines=(MembershipInline,ItemInline)
admin.site.register(ChecklistItem)
admin.site.register(ActivityEntry)

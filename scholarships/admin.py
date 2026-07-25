from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Scholarship, ScholarshipRequest


class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'name', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'name')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('education', 'discipline', 'prefecture')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('education', 'discipline', 'prefecture')}),
    )


class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ('scholarship_name', 'foundation_name', 'section', 'imported_at')
    list_filter = ('section', 'imported_at')
    search_fields = ('scholarship_name', 'foundation_name', 'designated_schools', 'designated_fields')
    readonly_fields = ('imported_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('section', 'foundation_name', 'scholarship_name')
        }),
        ('Contact Information', {
            'fields': ('address_contact', 'inquiry', 'application')
        }),
        ('Eligibility', {
            'fields': ('qualifier', 'designated_schools', 'designated_fields', 'plural_grants')
        }),
        ('Details', {
            'fields': ('additional_requirements', 'contents', 'duration', 'application_period', 'selection_method')
        }),
        ('Statistics', {
            'fields': ('grantees', 'grantees_applications')
        }),
        ('System', {
            'fields': ('imported_at',)
        }),
    )


class ScholarshipRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'scholarship', 'status', 'created_at', 'reviewed_by')
    list_filter = ('status', 'created_at', 'reviewed_date')
    search_fields = ('user__name', 'user__email', 'scholarship__scholarship_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Request Information', {
            'fields': ('user', 'scholarship', 'status')
        }),
        ('Review', {
            'fields': ('admin_notes', 'reviewed_by', 'reviewed_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        updated = queryset.update(status='approved', reviewed_by=request.user, reviewed_date=timezone.now())
        self.message_user(request, f'{updated} requests successfully approved.')
    approve_requests.short_description = "Approve selected requests"
    
    def reject_requests(self, request, queryset):
        updated = queryset.update(status='rejected', reviewed_by=request.user, reviewed_date=timezone.now())
        self.message_user(request, f'{updated} requests successfully rejected.')
    reject_requests.short_description = "Reject selected requests"


# Try to unregister the default User admin, then register our custom one
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, UserAdmin)

# Register our models
admin.site.register(Scholarship, ScholarshipAdmin)
admin.site.register(ScholarshipRequest, ScholarshipRequestAdmin)

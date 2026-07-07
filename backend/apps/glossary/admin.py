from django.contrib import admin

from .models import GlossaryTerm


@admin.register(GlossaryTerm)
class GlossaryTermAdmin(admin.ModelAdmin):
    list_display = ('term', 'key', 'category', 'updated_at')
    list_filter = ('category',)
    search_fields = ('term', 'key', 'definition')
    readonly_fields = ('created_at', 'updated_at')

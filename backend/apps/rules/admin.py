from django.contrib import admin

from .models import Rule, RuleCategory


@admin.register(RuleCategory)
class RuleCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'chapter_ref', 'source', 'sort_order')
    list_filter = ('source',)
    search_fields = ('name', 'slug', 'chapter_ref')
    ordering = ('sort_order', 'id')


@admin.register(Rule)
class RuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'rule_type', 'category', 'status', 'chapter_ref', 'updated_at')
    list_filter = ('rule_type', 'status', 'source', 'category')
    search_fields = ('title', 'slug', 'summary', 'content')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('sort_order', 'id')

from django.contrib import admin

from .models import Rule, RuleBook, RuleCategory, RuleChapter, RuleContentBlock, RuleEntry, RuleSection


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


class RuleContentBlockInline(admin.TabularInline):
    model = RuleContentBlock
    extra = 0
    fields = ('block_type', 'content', 'renderer_hint', 'sort_order')


@admin.register(RuleBook)
class RuleBookAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'version', 'status', 'source', 'updated_at')
    list_filter = ('status', 'source')
    search_fields = ('title', 'slug', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('title', 'id')


@admin.register(RuleChapter)
class RuleChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'rulebook', 'number', 'source_key', 'sort_order')
    list_filter = ('rulebook',)
    search_fields = ('title', 'slug', 'source_key', 'summary')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('rulebook', 'sort_order', 'id')
    inlines = (RuleContentBlockInline,)


@admin.register(RuleSection)
class RuleSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'chapter', 'parent', 'section_type', 'renderer_type', 'sort_order')
    list_filter = ('section_type', 'chapter')
    search_fields = ('title', 'slug', 'source_key', 'data_source', 'data_path', 'summary')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('chapter', 'sort_order', 'id')
    inlines = (RuleContentBlockInline,)


@admin.register(RuleEntry)
class RuleEntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'entry_type', 'section', 'category', 'source', 'sort_order')
    list_filter = ('entry_type', 'source', 'category')
    search_fields = ('title', 'slug', 'source_key', 'summary', 'content')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('sort_order', 'id')
    filter_horizontal = ('related_rules',)
    inlines = (RuleContentBlockInline,)


@admin.register(RuleContentBlock)
class RuleContentBlockAdmin(admin.ModelAdmin):
    list_display = ('block_type', 'chapter', 'section', 'entry', 'renderer_hint', 'sort_order')
    list_filter = ('block_type', 'renderer_hint')
    search_fields = ('content', 'renderer_hint')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('sort_order', 'id')

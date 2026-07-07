from rest_framework import serializers

from .models import Rule, RuleBook, RuleCategory, RuleChapter, RuleContentBlock, RuleEntry, RuleSection


class RuleCategorySerializer(serializers.ModelSerializer):
    parent_slug = serializers.CharField(source='parent.slug', read_only=True)

    class Meta:
        model = RuleCategory
        fields = [
            'id',
            'name',
            'slug',
            'parent',
            'parent_slug',
            'chapter_ref',
            'source',
            'sort_order',
            'metadata',
        ]


class RuleListSerializer(serializers.ModelSerializer):
    category = RuleCategorySerializer(read_only=True)

    class Meta:
        model = Rule
        fields = [
            'id',
            'title',
            'slug',
            'summary',
            'rule_type',
            'category',
            'chapter_ref',
            'source',
            'version_status',
            'status',
            'updated_at',
        ]


class RuleDetailSerializer(RuleListSerializer):
    class Meta(RuleListSerializer.Meta):
        fields = RuleListSerializer.Meta.fields + ['content', 'content_blocks', 'raw_data']


class RuleContentBlockSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='block_type', read_only=True)

    class Meta:
        model = RuleContentBlock
        fields = [
            'id',
            'type',
            'block_type',
            'content',
            'data',
            'renderer_hint',
            'sort_order',
            'metadata',
        ]


class RuleBookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleBook
        fields = [
            'id',
            'title',
            'slug',
            'version',
            'status',
            'source',
            'description',
            'updated_at',
        ]


class RuleBookDetailSerializer(RuleBookListSerializer):
    class Meta(RuleBookListSerializer.Meta):
        fields = RuleBookListSerializer.Meta.fields + ['metadata']


class RuleSectionTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = RuleSection
        fields = [
            'id',
            'title',
            'slug',
            'section_type',
            'summary',
            'source_key',
            'data_source',
            'data_path',
            'renderer_type',
            'sort_order',
            'children',
        ]

    def get_children(self, obj):
        children = obj.children.all().order_by('sort_order', 'id')
        return RuleSectionTreeSerializer(children, many=True).data


class RuleChapterTreeSerializer(serializers.ModelSerializer):
    sections = serializers.SerializerMethodField()

    class Meta:
        model = RuleChapter
        fields = [
            'id',
            'title',
            'slug',
            'number',
            'summary',
            'source_key',
            'sort_order',
            'sections',
        ]

    def get_sections(self, obj):
        sections = obj.sections.filter(parent__isnull=True).order_by('sort_order', 'id')
        return RuleSectionTreeSerializer(sections, many=True).data


class RuleEntryListSerializer(serializers.ModelSerializer):
    category = RuleCategorySerializer(read_only=True)

    class Meta:
        model = RuleEntry
        fields = [
            'id',
            'title',
            'slug',
            'entry_type',
            'summary',
            'source',
            'source_key',
            'sort_order',
            'tags',
            'category',
        ]


class RuleEntryDetailSerializer(RuleEntryListSerializer):
    section = RuleSectionTreeSerializer(read_only=True)
    content_blocks = RuleContentBlockSerializer(many=True, read_only=True)
    related_rules = RuleEntryListSerializer(many=True, read_only=True)

    class Meta(RuleEntryListSerializer.Meta):
        fields = RuleEntryListSerializer.Meta.fields + [
            'section',
            'content',
            'content_blocks',
            'related_rules',
            'metadata',
        ]


class RuleChapterDetailSerializer(serializers.ModelSerializer):
    content_blocks = RuleContentBlockSerializer(many=True, read_only=True)
    sections = serializers.SerializerMethodField()

    class Meta:
        model = RuleChapter
        fields = [
            'id',
            'title',
            'slug',
            'number',
            'summary',
            'source_key',
            'sort_order',
            'metadata',
            'content_blocks',
            'sections',
        ]

    def get_sections(self, obj):
        sections = obj.sections.filter(parent__isnull=True).order_by('sort_order', 'id')
        return RuleSectionTreeSerializer(sections, many=True).data


class RuleSectionDetailSerializer(RuleSectionTreeSerializer):
    children = serializers.SerializerMethodField()
    entries = serializers.SerializerMethodField()
    content_blocks = RuleContentBlockSerializer(many=True, read_only=True)

    class Meta(RuleSectionTreeSerializer.Meta):
        fields = RuleSectionTreeSerializer.Meta.fields + [
            'metadata',
            'content_blocks',
            'entries',
        ]

    def get_children(self, obj):
        children = obj.children.all().order_by('sort_order', 'id')
        return RuleSectionTreeSerializer(children, many=True).data

    def get_entries(self, obj):
        entries = obj.entries.all().order_by('sort_order', 'id')
        return RuleEntryListSerializer(entries, many=True).data

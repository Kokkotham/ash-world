from rest_framework import serializers

from .models import Rule, RuleCategory


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

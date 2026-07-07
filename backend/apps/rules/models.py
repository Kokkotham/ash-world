from django.db import models

from apps.common.models import TimeStampedModel


class RuleCategory(TimeStampedModel):
    name = models.CharField('分类名称', max_length=100)
    slug = models.SlugField('分类标识', max_length=120, unique=True)
    parent = models.ForeignKey(
        'self',
        verbose_name='父分类',
        null=True,
        blank=True,
        related_name='children',
        on_delete=models.SET_NULL,
    )
    chapter_ref = models.CharField('章节号', max_length=50, blank=True, default='')
    source = models.CharField('来源', max_length=50, blank=True, default='core')
    sort_order = models.IntegerField('排序', default=0)
    metadata = models.JSONField('扩展数据', default=dict, blank=True)

    class Meta:
        verbose_name = '规则分类'
        verbose_name_plural = '规则分类'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class Rule(TimeStampedModel):
    class RuleType(models.TextChoices):
        PROFESSION = 'profession', '专修'
        DIVINE_ART = 'divine_art', '神术'
        STORY_RULE = 'story_rule', '故事运作'
        ATTRIBUTE = 'attribute', '属性系统'
        OTHER = 'other', '其他'

    class Status(models.TextChoices):
        DRAFT = 'draft', '草稿'
        PUBLISHED = 'published', '已发布'

    title = models.CharField('标题', max_length=200)
    slug = models.SlugField('规则标识', max_length=220, unique=True)
    summary = models.TextField('摘要', blank=True, default='')
    content = models.TextField('可渲染正文', blank=True, default='')
    content_blocks = models.JSONField('结构化正文', default=list, blank=True)
    raw_data = models.JSONField('原始数据', default=dict, blank=True)
    rule_type = models.CharField('规则类型', max_length=50, choices=RuleType.choices, default=RuleType.OTHER)
    category = models.ForeignKey(
        RuleCategory,
        verbose_name='分类',
        null=True,
        blank=True,
        related_name='rules',
        on_delete=models.SET_NULL,
    )
    chapter_ref = models.CharField('章节号', max_length=50, blank=True, default='')
    source = models.CharField('来源', max_length=50, blank=True, default='core')
    version_status = models.CharField('版本状态', max_length=50, blank=True, default='')
    status = models.CharField('发布状态', max_length=20, choices=Status.choices, default=Status.PUBLISHED)
    sort_order = models.IntegerField('排序', default=0)

    class Meta:
        verbose_name = '规则条目'
        verbose_name_plural = '规则条目'
        ordering = ['sort_order', 'id']
        indexes = [
            models.Index(fields=['rule_type', 'status']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

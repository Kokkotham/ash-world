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


class RuleBook(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = 'draft', '草稿'
        PUBLISHED = 'published', '已发布'
        ARCHIVED = 'archived', '已归档'

    title = models.CharField('规则书标题', max_length=200)
    slug = models.SlugField('规则书标识', max_length=220, unique=True)
    version = models.CharField('版本', max_length=50, blank=True, default='')
    status = models.CharField('发布状态', max_length=20, choices=Status.choices, default=Status.DRAFT)
    source = models.CharField('来源', max_length=100, blank=True, default='core')
    description = models.TextField('说明', blank=True, default='')
    raw_data = models.JSONField('原始数据', default=dict, blank=True)
    metadata = models.JSONField('扩展数据', default=dict, blank=True)

    class Meta:
        verbose_name = '规则书'
        verbose_name_plural = '规则书'
        ordering = ['title', 'id']

    def __str__(self):
        return self.title


class RuleChapter(TimeStampedModel):
    rulebook = models.ForeignKey(
        RuleBook,
        verbose_name='规则书',
        related_name='chapters',
        on_delete=models.CASCADE,
    )
    title = models.CharField('章节标题', max_length=200)
    slug = models.SlugField('章节标识', max_length=220)
    number = models.CharField('章节号', max_length=50, blank=True, default='')
    summary = models.TextField('摘要', blank=True, default='')
    source_key = models.CharField('源数据标识', max_length=220, blank=True, default='')
    sort_order = models.IntegerField('排序', default=0)
    raw_data = models.JSONField('原始数据', default=dict, blank=True)
    metadata = models.JSONField('扩展数据', default=dict, blank=True)

    class Meta:
        verbose_name = '规则书章节'
        verbose_name_plural = '规则书章节'
        ordering = ['rulebook', 'sort_order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['rulebook', 'slug'], name='unique_rule_chapter_slug_per_book'),
        ]
        indexes = [
            models.Index(fields=['rulebook', 'sort_order']),
            models.Index(fields=['slug']),
            models.Index(fields=['source_key']),
        ]

    def __str__(self):
        return self.title


class RuleSection(TimeStampedModel):
    class SectionType(models.TextChoices):
        TEXT = 'text', '文本'
        DATA = 'data', '数据'
        GROUP = 'group', '分组'
        OTHER = 'other', '其他'

    chapter = models.ForeignKey(
        RuleChapter,
        verbose_name='所属章节',
        related_name='sections',
        on_delete=models.CASCADE,
    )
    parent = models.ForeignKey(
        'self',
        verbose_name='父小节',
        null=True,
        blank=True,
        related_name='children',
        on_delete=models.CASCADE,
    )
    title = models.CharField('小节标题', max_length=200)
    slug = models.SlugField('小节标识', max_length=260)
    section_type = models.CharField('小节类型', max_length=50, choices=SectionType.choices, default=SectionType.TEXT)
    summary = models.TextField('摘要', blank=True, default='')
    source_key = models.CharField('源数据标识', max_length=220, blank=True, default='')
    data_source = models.CharField('数据源', max_length=220, blank=True, default='')
    data_path = models.CharField('数据路径', max_length=260, blank=True, default='')
    renderer_type = models.CharField('渲染类型', max_length=120, blank=True, default='')
    sort_order = models.IntegerField('排序', default=0)
    raw_data = models.JSONField('原始数据', default=dict, blank=True)
    metadata = models.JSONField('扩展数据', default=dict, blank=True)

    class Meta:
        verbose_name = '规则书小节'
        verbose_name_plural = '规则书小节'
        ordering = ['chapter', 'sort_order', 'id']
        constraints = [
            models.UniqueConstraint(fields=['chapter', 'slug'], name='unique_rule_section_slug_per_chapter'),
        ]
        indexes = [
            models.Index(fields=['chapter', 'parent', 'sort_order']),
            models.Index(fields=['slug']),
            models.Index(fields=['source_key']),
            models.Index(fields=['section_type']),
        ]

    def __str__(self):
        return self.title


class RuleEntry(TimeStampedModel):
    class EntryType(models.TextChoices):
        ATTRIBUTE = 'attribute', '属性'
        RACE = 'race', '种族'
        RULE = 'rule', '规则'
        TABLE = 'table', '表格'
        OTHER = 'other', '其他'

    section = models.ForeignKey(
        RuleSection,
        verbose_name='所属小节',
        null=True,
        blank=True,
        related_name='entries',
        on_delete=models.SET_NULL,
    )
    category = models.ForeignKey(
        RuleCategory,
        verbose_name='规则分类',
        null=True,
        blank=True,
        related_name='rulebook_entries',
        on_delete=models.SET_NULL,
    )
    title = models.CharField('条目标题', max_length=220)
    slug = models.SlugField('条目标识', max_length=280, unique=True)
    entry_type = models.CharField('条目类型', max_length=50, choices=EntryType.choices, default=EntryType.OTHER)
    summary = models.TextField('摘要', blank=True, default='')
    content = models.TextField('可渲染正文', blank=True, default='')
    source = models.CharField('来源', max_length=100, blank=True, default='core')
    source_key = models.CharField('源数据标识', max_length=220, blank=True, default='')
    sort_order = models.IntegerField('排序', default=0)
    tags = models.JSONField('标签', default=list, blank=True)
    related_rules = models.ManyToManyField(
        'self',
        verbose_name='相关规则',
        symmetrical=False,
        blank=True,
        related_name='referenced_by',
    )
    raw_data = models.JSONField('原始数据', default=dict, blank=True)
    metadata = models.JSONField('扩展数据', default=dict, blank=True)

    class Meta:
        verbose_name = '规则书条目'
        verbose_name_plural = '规则书条目'
        ordering = ['sort_order', 'id']
        indexes = [
            models.Index(fields=['entry_type']),
            models.Index(fields=['slug']),
            models.Index(fields=['source_key']),
            models.Index(fields=['section', 'sort_order']),
        ]

    def __str__(self):
        return self.title


class RuleContentBlock(TimeStampedModel):
    class BlockType(models.TextChoices):
        PARAGRAPH = 'paragraph', '段落'
        HEADING = 'heading', '标题'
        SUBHEADING = 'subheading', '小标题'
        TABLE = 'table', '表格'
        LIST = 'list', '列表'
        QUOTE = 'quote', '引用'
        PROFILE = 'profile', '资料块'
        STAT_BLOCK = 'stat_block', '数值块'
        ABILITY = 'ability', '能力'
        RAW_JSON = 'raw_json', '原始JSON'
        OTHER = 'other', '其他'

    chapter = models.ForeignKey(
        RuleChapter,
        verbose_name='所属章节',
        null=True,
        blank=True,
        related_name='content_blocks',
        on_delete=models.CASCADE,
    )
    section = models.ForeignKey(
        RuleSection,
        verbose_name='所属小节',
        null=True,
        blank=True,
        related_name='content_blocks',
        on_delete=models.CASCADE,
    )
    entry = models.ForeignKey(
        RuleEntry,
        verbose_name='所属条目',
        null=True,
        blank=True,
        related_name='content_blocks',
        on_delete=models.CASCADE,
    )
    block_type = models.CharField('内容块类型', max_length=50, choices=BlockType.choices, default=BlockType.PARAGRAPH)
    content = models.TextField('正文', blank=True, default='')
    data = models.JSONField('结构化数据', default=dict, blank=True)
    renderer_hint = models.CharField('渲染提示', max_length=120, blank=True, default='')
    sort_order = models.IntegerField('排序', default=0)
    raw_data = models.JSONField('原始数据', default=dict, blank=True)
    metadata = models.JSONField('扩展数据', default=dict, blank=True)

    class Meta:
        verbose_name = '规则书内容块'
        verbose_name_plural = '规则书内容块'
        ordering = ['sort_order', 'id']
        indexes = [
            models.Index(fields=['chapter', 'sort_order']),
            models.Index(fields=['section', 'sort_order']),
            models.Index(fields=['entry', 'sort_order']),
            models.Index(fields=['block_type']),
        ]

    def __str__(self):
        owner = self.entry or self.section or self.chapter
        return f'{owner}: {self.block_type}'

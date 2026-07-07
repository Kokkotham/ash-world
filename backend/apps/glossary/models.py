from django.db import models

from apps.common.models import TimeStampedModel


class GlossaryTerm(TimeStampedModel):
    key = models.SlugField('术语标识', max_length=120, unique=True)
    term = models.CharField('术语名称', max_length=120)
    category = models.CharField('分类', max_length=100, blank=True, default='')
    definition = models.TextField('定义')
    aliases = models.JSONField('别名', default=list, blank=True)
    related_keys = models.JSONField('关联术语', default=list, blank=True)

    class Meta:
        verbose_name = '术语词条'
        verbose_name_plural = '术语词条'
        ordering = ['category', 'term']
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.term

from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets

from .models import Rule, RuleBook, RuleCategory, RuleChapter, RuleEntry, RuleSection
from .serializers import (
    RuleBookDetailSerializer,
    RuleBookListSerializer,
    RuleCategorySerializer,
    RuleChapterDetailSerializer,
    RuleChapterTreeSerializer,
    RuleDetailSerializer,
    RuleEntryDetailSerializer,
    RuleListSerializer,
    RuleSectionDetailSerializer,
)


class RuleCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RuleCategory.objects.all()
    serializer_class = RuleCategorySerializer
    lookup_field = 'slug'


class RuleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Rule.objects.select_related('category').all()
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RuleDetailSerializer
        return RuleListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        rule_type = self.request.query_params.get('type')
        category = self.request.query_params.get('category')
        keyword = self.request.query_params.get('q')
        if rule_type:
            queryset = queryset.filter(rule_type=rule_type)
        if category:
            queryset = queryset.filter(category__slug=category)
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword)
                | Q(summary__icontains=keyword)
                | Q(content__icontains=keyword)
            )
        return queryset


class RuleBookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RuleBook.objects.all()
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RuleBookDetailSerializer
        return RuleBookListSerializer

    @action(detail=True, methods=['get'])
    def chapters(self, request, slug=None):
        rulebook = self.get_object()
        chapters = rulebook.chapters.all().order_by('sort_order', 'id')
        serializer = RuleChapterTreeSerializer(chapters, many=True)
        return Response({
            'rulebook': RuleBookListSerializer(rulebook).data,
            'chapters': serializer.data,
        })


class RuleChapterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RuleChapter.objects.prefetch_related('sections', 'content_blocks').all()
    serializer_class = RuleChapterDetailSerializer
    lookup_field = 'slug'


class RuleSectionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RuleSection.objects.select_related('chapter', 'parent').prefetch_related(
        'children',
        'entries',
        'content_blocks',
    ).all()
    serializer_class = RuleSectionDetailSerializer
    lookup_field = 'slug'


class RuleEntryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RuleEntry.objects.select_related('section', 'category').prefetch_related(
        'content_blocks',
        'related_rules',
    ).all()
    serializer_class = RuleEntryDetailSerializer
    lookup_field = 'slug'

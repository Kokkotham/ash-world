from django.db.models import Q
from rest_framework import viewsets

from .models import Rule, RuleCategory
from .serializers import RuleCategorySerializer, RuleDetailSerializer, RuleListSerializer


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

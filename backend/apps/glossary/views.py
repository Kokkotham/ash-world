from django.db.models import Q
from rest_framework import viewsets

from .models import GlossaryTerm
from .serializers import GlossaryTermSerializer


class GlossaryTermViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GlossaryTerm.objects.all()
    serializer_class = GlossaryTermSerializer
    lookup_field = 'key'

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        keyword = self.request.query_params.get('q')
        if category:
            queryset = queryset.filter(category=category)
        if keyword:
            queryset = queryset.filter(
                Q(term__icontains=keyword)
                | Q(key__icontains=keyword)
                | Q(definition__icontains=keyword)
            )
        return queryset

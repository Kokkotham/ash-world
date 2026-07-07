from rest_framework import serializers

from .models import GlossaryTerm


class GlossaryTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlossaryTerm
        fields = [
            'id',
            'key',
            'term',
            'category',
            'definition',
            'aliases',
            'related_keys',
            'updated_at',
        ]

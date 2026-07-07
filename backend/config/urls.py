from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.glossary.views import GlossaryTermViewSet
from apps.rules.views import (
    RuleBookViewSet,
    RuleCategoryViewSet,
    RuleChapterViewSet,
    RuleEntryViewSet,
    RuleSectionViewSet,
    RuleViewSet,
)


router = DefaultRouter()
router.register('rule-categories', RuleCategoryViewSet, basename='rule-category')
router.register('rules', RuleViewSet, basename='rule')
router.register('rulebooks', RuleBookViewSet, basename='rulebook')
router.register('rulebook-chapters', RuleChapterViewSet, basename='rulebook-chapter')
router.register('rulebook-sections', RuleSectionViewSet, basename='rulebook-section')
router.register('rulebook-entries', RuleEntryViewSet, basename='rulebook-entry')
router.register('glossary', GlossaryTermViewSet, basename='glossary')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
]

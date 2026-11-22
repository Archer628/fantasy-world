from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'worlds', views.WorldViewSet, basename='world')
router.register(r'factions', views.FactionViewSet, basename='faction')
router.register(r'characters', views.CharacterViewSet, basename='character')
router.register(r'artifact-categories', views.ArtifactCategoryViewSet, basename='artifact-category')
router.register(r'artifacts', views.ArtifactViewSet, basename='artifact')
router.register(r'ability-systems', views.AbilitySystemViewSet, basename='ability-system')
router.register(r'realms', views.RealmViewSet, basename='realm')
router.register(r'skill-levels', views.SkillLevelViewSet, basename='skill-level')
router.register(r'skills', views.SkillViewSet, basename='skill')
router.register(r'creatures', views.CreatureViewSet, basename='creature')
router.register(r'fragment-worlds', views.FragmentWorldViewSet, basename='fragment-world')
router.register(r'historical-events', views.HistoricalEventViewSet, basename='historical-event')
router.register(r'relationships', views.RelationshipViewSet, basename='relationship')
router.register(r'lore-pages', views.LorePageViewSet, basename='lore-page')
router.register(r'origin-laws', views.OriginLawViewSet, basename='origin-law')
router.register(r'anomalies', views.AnomalyViewSet, basename='anomaly')

urlpatterns = [
    path('search/', views.global_search, name='global-search'),
    path('stats/', views.world_stats, name='world-stats'),
    path('', include(router.urls)),
]

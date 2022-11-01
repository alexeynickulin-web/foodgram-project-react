from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CreateUserView, ShoppingCartInList, FavoriteViewSet,
                    IngredientViewSet, RecipeViewSet, ShoppingCartViewSet,
                    FollowViewSet, TagViewSet)

app_name = 'api'
router = DefaultRouter()


router.register('users', CreateUserView, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('users/subscriptions/',
         FollowViewSet.as_view({'get': 'list'}), name='subscriptions'),
    path('recipes/download_shopping_cart/',
         ShoppingCartInList.as_view({'get': 'download'}), name='download'),
    path('users/<int:users_id>/subscribe/',
         FollowViewSet.as_view({'post': 'create',
                                'delete': 'delete'}), name='subscribe'),
    path('recipes/<int:recipes_id>/favorite/',
         FavoriteViewSet.as_view({'post': 'create',
                                  'delete': 'delete'}), name='favorite'),
    path('recipes/<int:recipes_id>/shopping_cart/',
         ShoppingCartViewSet.as_view({'post': 'create',
                                     'delete': 'delete'}), name='cart'),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

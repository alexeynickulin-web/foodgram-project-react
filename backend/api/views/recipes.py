import io

from django.db.models import Sum
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics, ttfonts
from reportlab.pdfgen import canvas
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.filters import RecipeFilter
from api.serializers.recipes import (FavoriteSerializer, IngredientSerializer,
                                     RecipeSerializer, RecipeSerializerWrite,
                                     ShoppingCartSerializer, TagSerializer)
from api.serializers.users import RecipeShortSerializer
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag

FILENAME = 'my_shopping_cart.pdf'


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name__startswith=name)
        return queryset


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeSerializerWrite
        return RecipeSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, **kwargs):
        """Позволяет текущему пользователю добавить/удалить
        рецепт в список избранных"""

        target_recipe = int(kwargs['pk'])
        recipe = get_object_or_404(Recipe, id=target_recipe)
        if request.method == 'DELETE':
            favorite = get_object_or_404(
                Favorite, user=request.user, recipe=recipe
            )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = FavoriteSerializer(
            data={'user': request.user.id, 'recipe': recipe.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        represent_serializer = RecipeShortSerializer(
            recipe, context={'request': request}
        )
        return Response(
            represent_serializer.data, status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, **kwargs):
        """Позволяет текущему пользователю добавить/удалить
        рецепт в список покупок"""

        target_recipe = int(kwargs['pk'])
        recipe = get_object_or_404(Recipe, id=target_recipe)
        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                    user=request.user, recipe=recipe
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже добавили этот sрецепт в корзину'
                )

            serializer = ShoppingCartSerializer(
                data={'user': request.user.id, 'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            represent_serializer = RecipeShortSerializer(
                recipe, context={'request': request}
            )
            return Response(
                represent_serializer.data, status=status.HTTP_201_CREATED
            )
        delete_obj = get_object_or_404(
            ShoppingCart, user=request.user, recipe=recipe
        )
        delete_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Позволяет текущему пользователю получить
        список ингредиентов для покупки"""

        if not request.user.is_authenticated:
            return Response(
                {'Пользователь не авторизован'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        buffer = io.BytesIO()
        page = canvas.Canvas(buffer)
        arial = ttfonts.TTFont('Arial', 'fonts/arial.ttf')
        pdfmetrics.registerFont(arial)

        x_position, y_position = 50, 800

        user_shopping_cart = request.user.shopping_cart.values(
            'recipe__ingredients__name',
            'recipe__ingredients__measurement_unit'
        ).annotate(amount=Sum('recipe__recipe_ingredients__amount'))
        page.setFont('Arial', 14)

        if user_shopping_cart:
            indent = 20
            page.drawString(x_position, y_position, 'Cписок покупок:')
            for index, ingredient in enumerate(user_shopping_cart, start=1):
                string = (f'{index}. '
                          f'{ingredient["recipe__ingredients__name"]} -')
                string += f'{ingredient["amount"]} '
                string += (
                    f'{ingredient["recipe__ingredients__measurement_unit"]}'
                )
                page.drawString(
                    x_position, y_position - indent,
                    string)
                y_position -= 15
                if y_position <= 50:
                    page.showPage()
                    y_position = 800
            page.save()
            buffer.seek(0)
            return FileResponse(
                buffer, as_attachment=True, filename=FILENAME)
        page.setFont('Arial', 14)
        page.drawString(
            x_position,
            y_position,
            'Cписок покупок пуст!')
        page.save()
        buffer.seek(0)

        return HttpResponse(buffer, content_type='application/pdf')

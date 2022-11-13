import djoser.views
from django.shortcuts import get_object_or_404
from djoser.conf import settings
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.serializers.users import (CustomUserCreateSerializer,
                                   CustomUserSerializer, SubscribeSerializer,
                                   SubscriptionShowSerializer)
from users.models import Follow, User


class UserViewSet(djoser.views.UserViewSet):

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscribe(self, request, **kwargs):
        """Позволяет текущему пользователю подписываться/отписываться от
        от автора контента, чей профиль он просматривает."""

        target_user = int(kwargs['id'])
        author = get_object_or_404(User, id=target_user)
        if request.method == 'DELETE':
            subscription = get_object_or_404(
                Follow, user=request.user, following=author
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = SubscribeSerializer(
            data={'user': request.user.id, 'following': author.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        author_serializer = SubscriptionShowSerializer(
            author, context={'request': request}
        )
        return Response(
            author_serializer.data, status=status.HTTP_201_CREATED
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated,)
    )
    def subscriptions(self, request):
        """Позволяет текущему пользователю
        просмотреть свои подписки."""

        queryset = User.objects.filter(following__user=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            serializer.data, status=status.HTTP_200_OK
        )

    def get_serializer_class(self):
        if self.action in ['subscribe', 'subscriptions']:
            return SubscriptionShowSerializer
        if self.action == 'create':
            return CustomUserCreateSerializer
        if self.action == 'set_password':
            return settings.SERIALIZERS.set_password
        return CustomUserSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(self.request.query_params)
        return context

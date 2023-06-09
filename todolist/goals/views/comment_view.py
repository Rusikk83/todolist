from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters,generics,permissions

from goals.serializers import GoalCommentCreateSerializer, GoalCommentDetailSerializer

from goals.models import GoalComment
from goals.permissions import GoalCommentPermission


""" представление для создания коментария"""


class GoalCommentCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentCreateSerializer


""" представление для получения списка категорий пользователя"""


class GoalCommentListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentDetailSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['goal']
    ordering = ['-created']

    def get_queryset(self) -> QuerySet[GoalComment]:
        return GoalComment.objects.filter(goal__category__board__participants__user=self.request.user)  # выборка
        # комментариев по целям, которые размещены на досках с участником пользователем


""" представление для операций  по комментарию"""


class GoalCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [GoalCommentPermission]
    serializer_class = GoalCommentDetailSerializer

    def get_queryset(self) -> QuerySet[GoalComment]:
        return GoalComment.objects.select_related('user').filter(  # выборка комментариев для целей на досках,
            # для которых пользователь является участником
            goal__category__board__participants__user=self.request.user
        )





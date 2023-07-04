from django.db import transaction
from django.db.models import QuerySet
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import permissions, filters

from goals.models import GoalCategory

from goals.serializers import GoalCategoryCreateSerializer, GoalCategorySerializer
from rest_framework.pagination import LimitOffsetPagination

from goals.permissions import GoalCategoryPermission

from goals.models import Goal


""" представление для создания категории"""


class GoalCategoryCreateView(CreateAPIView):
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategoryCreateSerializer


""" представление для получения списка категорий пользователя"""


class GoalCategoryListView(ListAPIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategorySerializer

    pagination_class = LimitOffsetPagination
    filter_backends = [
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["title", "created"]
    ordering = ["title"]
    search_fields = ["title"]

    def get_queryset(self) -> QuerySet[GoalCategory]:
        return GoalCategory.objects.select_related('user').filter(  # получение категорий на досках для которых
            # пользователь является участником и категория не удалена
            board__participants__user=self.request.user, is_deleted=False
        )


""" представление для операций по категории"""


class GoalCategoryDetailView(RetrieveUpdateDestroyAPIView):

    serializer_class = GoalCategorySerializer
    permission_classes = [GoalCategoryPermission]

    queryset = GoalCategory.objects.filter(is_deleted=False)

    def perform_destroy(self, instance: GoalCategory) -> None:
        with transaction.atomic():  # транзакция для удаления категории с ее целями
            instance.is_deleted = True
            instance.goal_set.update(status=Goal.Status.archived)  # статус архив для целей категории
            instance.save(update_fields=['is_deleted'])


from django.db import transaction
from django.db.models import QuerySet
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import permissions, filters

from goals.models import GoalCategory

from goals.serializers import GoalCategoryCreateSerializer, GoalCategorySerializer
from rest_framework.pagination import LimitOffsetPagination

from goals.permissions import GoalCategoryPermission

from goals.models import Goal


class GoalCategoryCreateView(CreateAPIView):
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategoryCreateSerializer


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
        return GoalCategory.objects.select_related('user').filter(
            board__participants__user=self.request.user, is_deleted=False
        )


class GoalCategoryDetailView(RetrieveUpdateDestroyAPIView):

    serializer_class = GoalCategorySerializer
    permission_classes = [GoalCategoryPermission]

    queryset = GoalCategory.objects.filter(is_deleted=False)

    def perform_destroy(self, instance: GoalCategory) -> None:
        with transaction.atomic():
            instance.is_deleted = True
            instance.goal_set.update(status=Goal.Status.archived)
            instance.save(update_fields=['is_deleted'])


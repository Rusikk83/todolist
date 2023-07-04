from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions, filters

from goals.filters import GoalFilter

from goals.serializers import GoalCreateSerializer, GoalSerializer

from goals.models import Goal
from goals.permissions import GoalPermission

""" представление для создания цели"""


class GoalCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCreateSerializer


""" представление для получения списка целей пользователя"""


class GoalListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = GoalFilter
    ordering_fields = ['title', 'created']
    ordering = ['title']
    search_fields = ['title', 'description']

    def get_queryset(self) -> None:
        return Goal.objects.filter(
            category__board__participants__user=self.request.user,  # выборка целей на досках,
            # для которых пользователь является участником
        ).exclude(status=Goal.Status.archived)


""" представление для операций с целью"""


class GoalDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [GoalPermission]
    serializer_class = GoalSerializer
    queryset = Goal.objects.exclude(status=Goal.Status.archived)

    def perform_destroy(self, instance: Goal) -> None:
        instance.status = Goal.Status.archived  # признак архивации вместо удаления цели
        instance.save(update_fields=['status'])

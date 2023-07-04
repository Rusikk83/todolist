from django.db import transaction
from django.db.models import QuerySet
from rest_framework import generics, filters, permissions

from goals.models import BoardParticipant, Board, Goal
from goals.permissions import BoardPermission
from goals.serializers import BoardSerializer, BoardDetailSerializer


""" представление для создания доски"""


class BoardCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardSerializer

    def perform_create(self, serializer: BoardSerializer) -> None:
        with transaction.atomic():
            board = serializer.save()
            BoardParticipant.objects.create(user=self.request.user, board=board, role=BoardParticipant.Role.owner)  #
            # создание доски, пользователь берется из запроса, роль - владелец



""" представление для получения списка досок пользователя"""


class BoardListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['title']

    def get_queryset(self) -> QuerySet[Board]:
        return Board.objects.filter(participants__user=self.request.user).exclude(is_deleted=True)  # получаем все доски
        # где пользователь участник и доска не удалена


""" представление для операций с доской"""


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [BoardPermission]
    serializer_class = BoardDetailSerializer
    queryset = Board.objects.prefetch_related('participants__user').exclude(is_deleted=True)

    def perform_destroy(self, instance: Board) -> None:
        with transaction.atomic():  # транзакция для удаления доски, ее категорий и целей
            Board.objects.filter(id=instance).update(is_deleted=True)
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(status=Goal.Status.archived)

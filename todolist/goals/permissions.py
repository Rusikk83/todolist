from typing import Any

from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant
from rest_framework.request import Request

""" разрешения для доски"""


class BoardPermission(IsAuthenticated):

    def has_object_permission(self, request: Request, view: GenericAPIView, obj: Board) -> bool:
        _filters: dict[str, Any] = {'user': request.user, 'board': obj}  # добавляем доску и пользователя в фильтр
        if request.method not in SAFE_METHODS:
            _filters['role'] = BoardParticipant.Role.owner  # для методов изменения добавляем роль в фильтр

        return BoardParticipant.objects.filter(**_filters).exists()  # определяем наличие выборки по фильтру


""" разрешения для категории """


class GoalCategoryPermission(IsAuthenticated):

    def has_object_permission(self, request: Request, view: GenericAPIView, obj: GoalCategory) -> bool:
        _filters: dict[str, Any] = {'user': request.user, 'board': obj.board}  # добавляем доску и пользователя в фильтр
        if request.method not in SAFE_METHODS:
            _filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]  # для методов изменения
            # добавляем роли в фильтр

        return BoardParticipant.objects.filter(**_filters).exists()  # определяем наличие выборки по фильтру


""" разрешения для цели """


class GoalPermission(IsAuthenticated):

    def has_object_permission(self, request: Request, view: GenericAPIView, obj: Goal) -> bool:
        _filters: dict[str, Any] = {'user': request.user, 'board': obj.category.board}  # добавляем доску
        # и пользователя в фильтр
        if request.method not in SAFE_METHODS:
            _filters['role__in'] = [BoardParticipant.Role.owner, BoardParticipant.Role.writer]  # для методов изменения
            # добавляем роли в фильтр

        return BoardParticipant.objects.filter(**_filters).exists()  # определяем наличие выборки по фильтру


""" разрешения для комментария """


class GoalCommentPermission(IsAuthenticated):

    def has_object_permission(self, request: Request, view: GenericAPIView, obj: GoalComment) -> bool:
        if request.method in SAFE_METHODS:
            return True  # методы без изменения доступны всем
        return obj.user == request.user  # методы изменения доступны только владельцу комментария

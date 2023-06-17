from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

from goals.models import GoalCategory, Goal, GoalComment
from rest_framework.request import Request


class GoalCategoryPermission(IsAuthenticated):

    def has_object_permission(self, request: Request, view: GenericAPIView, obj: GoalCategory) -> bool:
        return obj.user == request.user


class GoalPermission(IsAuthenticated):

    def has_object_permission(self, request: Request, view: GenericAPIView, obj: Goal) -> bool:
        return obj.user == request.user

class GoalCommentPermission(IsAuthenticated):

    def has_object_permission(self, request: Request, view: GenericAPIView, obj: GoalComment) -> bool:
        return obj.user == request.user
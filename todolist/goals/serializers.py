from django.db import transaction
from rest_framework import serializers
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant

from django.utils import timezone

from core.serializers import UserSerializer
from rest_framework.exceptions import ValidationError, PermissionDenied

from django.db.models import DateField

from core.models import User
from rest_framework.request import Request


class GoalCategoryCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_board(self, board: Board) -> Board:
        if board.is_deleted:
            raise ValidationError('board is deleted')  # если доска удалена

        if not BoardParticipant.objects.filter(
            board_id=board.id,
            role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
            user_id=self.context['request'].user
        ).exists():
            raise PermissionDenied  # если пользователь не участник с правом редактирования

        return board

    class Meta:
        model = GoalCategory
        read_only_fields = ("id", "created", "updated", "user", "is_deleted")
        fields = "__all__"


class GoalCategorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = GoalCategory
        fields = "__all__"
        read_only_fields = ("id", "created", "updated", "user", "is_deleted")


class GoalCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ("id", "created", "updated", "user")

    def validate_category(self, value: GoalCategory) -> GoalCategory:

        if not BoardParticipant.objects.filter(
                board_id=value.board_id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user_id=self.context['request'].user
        ).exists():
            raise PermissionDenied('mast be owner or writer role')  # если пользователь не участник доски
            # с правом редактирования

        if value.is_deleted:
            raise ValidationError('Category not found')  # если категория удалена

        return value

    def validate_due_date(self, value: DateField) -> DateField:
        if value < timezone.now().date():
            raise ValidationError("End-date can't be in the past")  # если дедлайн в прошедшем времени
        return value


class GoalSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ("id", "created", "updated", "user")


class GoalCommentCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ("id", "created", "updated", "user")

    def validate_goal(self, value: Goal) -> Goal:
        if value.status == Goal.Status.archived:
            raise ValidationError('Goal not found')
        if not BoardParticipant.objects.filter(
                board_id=value.category.board_id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                user_id=self.context['request'].user
        ).exists():
            raise PermissionDenied  # если пользователь не участник доски с правом редактирования
        return value


class GoalCommentDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    goal = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ("id", "created", "updated", "user")


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        read_only_fields = ("id", "created", "updated", 'is_deleted')
        fields = '__all__'


class BoardParticipantSerializer(serializers.ModelSerializer):

    role = serializers.ChoiceField(required=True, choices=BoardParticipant.editable_roles)
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = BoardParticipant
        read_only_fields = ("id", "created", "updated", 'board')
        fields = '__all__'

    def validate_user(self, user: User) -> User:
        if self.context['request'].user == user:
            raise ValidationError('Failed to change your role')  # изменить участие владельца нельзя
        return user


class BoardDetailSerializer(BoardSerializer):
    participants = BoardParticipantSerializer(many=True)

    def update(self, instance: Board, validated_data: dict) -> Board:
        request: Request = self.context['request']

        with transaction.atomic():
            BoardParticipant.objects.filter(board=instance).exclude(user=request.user).delete()  # удаляем участников
            # кроме владельца
            BoardParticipant.objects.bulk_create(  # создаем всех участников заново
                [
                    BoardParticipant(user=participant['user'], role=participant['role'], board=instance)
                    for participant in validated_data.get('participants', [])
                ],
                ignore_conflicts=True,
            )

            if title := validated_data.get('title'):  # если меняется описание доски
                instance.title = title

            instance.save()

        return instance

import factory.django
from django.utils import timezone

from core.models import User

from pytest_factoryboy import register

from goals.models import Board, BoardParticipant, GoalCategory, Goal, GoalComment

from bot.models import TgUser


@register
class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker('user_name')
    password = factory.Faker('password')

    class Meta:
        model = User

    @classmethod
    def _create(cls, model_class, *args, **kwargs) -> User:
        return User.objects.create_user(*args, **kwargs)


class DaresFactoryMixin(factory.django.DjangoModelFactory):
    created = factory.LazyFunction(timezone.now)
    updated = factory.LazyFunction(timezone.now)


@register
class BoardFactory(DaresFactoryMixin):
    title = factory.Faker('sentence')

    class Meta:
        model = Board

    @factory.post_generation
    def with_owner(self, create, owner, **kwargs):
        if owner:
            BoardParticipant.objects.create(board=self, user=owner, role=BoardParticipant.Role.owner)


@register
class BoardParticipantFactory(DaresFactoryMixin):
    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = BoardParticipant


@register
class GoalCategoryFactory(DaresFactoryMixin):
    title = factory.Faker('catch_phrase')
    user = factory.SubFactory(UserFactory)
    board = factory.SubFactory(BoardFactory)

    class Meta:
        model = GoalCategory


@register
class GoalFactory(DaresFactoryMixin):
    title = factory.Faker('catch_phrase')
    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(GoalCategoryFactory)

    class Meta:
        model = Goal


@register
class GoalCommentFactory(DaresFactoryMixin):
    user = factory.SubFactory(UserFactory)
    goal = factory.SubFactory(GoalFactory)
    text = factory.Faker('sentence')

    class Meta:
        model = GoalComment


class TgUserFactory(factory.django.DjangoModelFactory):
    chat_id = factory.Faker('random_int', min=1)

    @classmethod
    def _create(cls, model_class, *args, **kwargs) -> User:
        obj = TgUser.objects.create(*args, **kwargs)
        obj.update_verification_code()
        return obj

    class Meta:
        model = TgUser

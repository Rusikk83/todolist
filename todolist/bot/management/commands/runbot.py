from typing import Callable, Any

from django.core.management import BaseCommand

from bot.tg.client import TgClient

from bot.tg.schemas import Message

from bot.models import TgUser
from pydantic import BaseModel

from goals.models import Goal, GoalCategory, BoardParticipant


class FSMData(BaseModel):
    next_handler: Callable
    data: dict[str, Any] = {}



class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.tg_client = TgClient()
        self.clients: dict[int, FSMData] = {}

    def handle(self, *args, **options):
        offset = 0

        self.stdout.write(self.style.SUCCESS('Bot started'))
        while True:
            res = self.tg_client.get_update(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(item.message)
                print(item.message)

    def handle_message(self, msg: Message):
        print(msg.chat)
        tg_user, _ = TgUser.objects.get_or_create(chat_id=msg.chat.id)


        if tg_user.is_verified:
            self.handle_authorized_user(tg_user, msg)
        else:
            self.handle_unauthorized_user(tg_user, msg)

    def handle_authorized_user(self, tg_user: TgUser, msg: Message):
        if msg.text.startswith('/'):
            if msg.text == '/goals':
                self.handle_goals_command(tg_user, msg)

            elif msg.text == '/create':
                self.handle_create_command(tg_user, msg)

            elif msg.text == '/cancel':
                self.clients.pop(tg_user.chat_id, None)
                self.tg_client.send_message(tg_user.chat_id, 'Command canceled')

            else:
                self.tg_client.send_message(tg_user.chat_id, 'Command not found')

        elif tg_user.chat_id in self.clients:
            client = self.clients[tg_user.chat_id]
            client.next_handler(tg_user=tg_user, msg=msg, **client.data)

        else:
            self.tg_client.send_message(tg_user.chat_id, 'Please, input the command format')




        # self.tg_client.send_message(tg_user.chat_id, 'Authorized')

    def handle_goals_command(self, tg_user: TgUser, msg: Message):
        """Периписать под доски"""
        goals = Goal.objects.exclude(status=Goal.Status.archived).filter(
            category__board__participants__user=tg_user.user
        )
        if goals:

            text = 'Your goals:\n' + '\n'.join([f''
                                                f'id: {goal.id}\n'
                                                f'  board: {goal.category.board.title}\n'
                                                f'  category: {goal.category.title}\n'
                                                f'  goal: {goal.title}' for goal in goals])
        else:
            text = 'You have not goals'

        self.tg_client.send_message(tg_user.chat_id, text)


    def handle_create_command(self, tg_user: TgUser, msg: Message):
        categories = GoalCategory.objects.filter(
            # выбираем категории размещенные на досках, для которых текущий пользователь участник
            board__participants__user=tg_user.user,
            # проверяем допустимость роли пользователя
            board__participants__role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        ).exclude(is_deleted=True)
        # print(categories, tg_user.user.id)
        if not categories:
            self.tg_client.send_message(tg_user.chat_id, 'You have not categories')
            return

        text = 'Select category to create goal:\n' + '\n'.join([f'{cat.id}) {cat.board.title}/{cat.title}'
                                                                for cat in categories])
        self.tg_client.send_message(tg_user.chat_id, text)
        self.clients[tg_user.chat_id] = FSMData(next_handler=self._get_category)

    def _get_category(self, tg_user: TgUser, msg: Message, **kwargs):
        try:
            category = GoalCategory.objects.filter(
                is_deleted=False,  # фильтруем не удаленные категории
                # фильтруем строки с соответствующими ролями участников досок
                board__participants__role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                # фильтруем строки только для текущего пользователя
                board__participants__user=tg_user.user
            ).get(pk=msg.text)  # проверяем допустимость введенного id

        except GoalCategory.DoesNotExist:
            self.tg_client.send_message(tg_user.chat_id, 'Category not available')
            return

        else:
            self.clients[tg_user.chat_id].next_handler = self._create_goal
            self.clients[tg_user.chat_id].data['category'] = category
            self.tg_client.send_message(tg_user.chat_id, 'Set goal title')


    def _create_goal(self, tg_user: TgUser, msg: Message, **kwargs):
        category = kwargs['category']
        new_goal = Goal.objects.create(category=category, user=tg_user.user, title=msg.text)
        self.tg_client.send_message(tg_user.chat_id, 'NewGoalCreated')
        self.clients.pop(tg_user.chat_id, None)


    def handle_unauthorized_user(self,  tg_user: TgUser, msg: Message):

        self.tg_client.send_message(tg_user.chat_id, 'Hello')
        tg_user.update_verification_code()
        self.tg_client.send_message(tg_user.chat_id, f'You verification code:\n{tg_user.verification_code}')

from typing import Callable, Any
from pydantic import BaseModel

from django.core.management import BaseCommand

from bot.tg.client import TgClient
from bot.tg.schemas import Message
from bot.models import TgUser
from goals.models import Goal, GoalCategory, BoardParticipant


class FSMData(BaseModel):
    next_handler: Callable
    data: dict[str, Any] = {}


class Command(BaseCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient()
        self.clients: dict[int, FSMData] = {}

    """ основная функция телеграмм-бота получает сообщения из чата бота и передает их в обрабатывающую функцию"""
    def handle(self, *args, **options):
        offset = 0

        self.stdout.write(self.style.SUCCESS('Bot started'))
        while True:
            res = self.tg_client.get_update(offset=offset)
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(item.message)
                # print(item.message)

    """ 
    функция обработки сообщений пользователей, определяет авторизован пользователь или нет
    и вызывает соответствующие функции
    """
    def handle_message(self, msg: Message) -> None:
        print(msg.chat)
        tg_user, _ = TgUser.objects.get_or_create(chat_id=msg.chat.id)

        if tg_user.is_verified:
            self.handle_authorized_user(tg_user, msg)
        else:
            self.handle_unauthorized_user(tg_user, msg)

    """функция обработки сообщений от авторизованных пользователей"""
    def handle_authorized_user(self, tg_user: TgUser, msg: Message) -> None:
        if str(msg.text).startswith('/'):  # если сообщение начинается со слеша
            if msg.text == '/goals':
                self.handle_goals_command(tg_user, msg)  # отправить цели пользователя

            elif msg.text == '/create':
                self.handle_create_command(tg_user, msg)  # создать цель пользователя

            elif msg.text == '/cancel':
                self.clients.pop(tg_user.chat_id, None)  # очищаем кеш состояний пользователя
                self.tg_client.send_message(tg_user.chat_id, 'Command canceled')

            else:
                self.tg_client.send_message(tg_user.chat_id, 'Command not found')  # если команда не распознана

        elif tg_user.chat_id in self.clients:  # если не команда и есть история состояний клиента
            client = self.clients[tg_user.chat_id]
            client.next_handler(tg_user=tg_user, msg=msg, **client.data)  # переход к следующему состоянию

        else:  # если не команда и нет истории состояний
            self.tg_client.send_message(tg_user.chat_id, 'Please, input the command format')

    """функция отправки целей пользователя в чат"""
    def handle_goals_command(self, tg_user: TgUser, msg: Message) -> None:

        goals = Goal.objects.exclude(status=Goal.Status.archived).filter(    # выбираем цели пользователя
            category__board__participants__user=tg_user.user
        )
        if goals:  # если цели найдены формируем текст с целями

            text = 'Your goals:\n' + '\n'.join([f''
                                                f'id: {goal.id}\n'
                                                f'  board: {goal.category.board.title}\n'
                                                f'  category: {goal.category.title}\n'
                                                f'  goal: {goal.title}' for goal in goals])
        else:
            text = 'You have not goals'    # текст - цели не найдены

        self.tg_client.send_message(tg_user.chat_id, text)  # отправляем сообщение

    """функция обработки команды создания цели"""
    def handle_create_command(self, tg_user: TgUser, msg: Message) -> None:
        # выбор доступных категорий пользователя
        categories = GoalCategory.objects.filter(
            # выбираем категории размещенные на досках, для которых текущий пользователь участник
            board__participants__user=tg_user.user,
            # проверяем допустимость роли пользователя
            board__participants__role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        ).exclude(is_deleted=True)

        if not categories:
            self.tg_client.send_message(tg_user.chat_id, 'You have not categories')  # сообщение если нет категорий
            return

        text = 'Select category to create goal:\n' + '\n'.join([f'{cat.id}) {cat.board.title}/{cat.title}'
                                                                for cat in categories])  # список категорий
        self.tg_client.send_message(tg_user.chat_id, text)  # отправляем сообщение с категориями
        self.clients[tg_user.chat_id] = FSMData(next_handler=self._get_category)  # следующее состояние пользователя

    """функция получения категории по введенному пользователем идентификатору"""
    def _get_category(self, tg_user: TgUser, msg: Message, **kwargs) -> None:
        try:
            category = GoalCategory.objects.filter(
                is_deleted=False,  # фильтруем не удаленные категории
                # фильтруем строки с соответствующими ролями участников досок
                board__participants__role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer],
                # фильтруем строки только для текущего пользователя
                board__participants__user=tg_user.user
            ).get(pk=msg.text)  # проверяем допустимость введенного id

        except GoalCategory.DoesNotExist:  # если категория не найдена для пользователя
            self.tg_client.send_message(tg_user.chat_id, 'Category not available')  # сообщение пользователю
            return

        else:  # категория найдена
            self.clients[tg_user.chat_id].next_handler = self._create_goal  # следующее состояние
            self.clients[tg_user.chat_id].data['category'] = category  # категория состояния
            self.tg_client.send_message(tg_user.chat_id, 'Set goal title')  # сообщение пользователю

    """функция создания цели"""
    def _create_goal(self, tg_user: TgUser, msg: Message, **kwargs) -> None:
        category = kwargs['category']
        new_goal = Goal.objects.create(category=category, user=tg_user.user, title=msg.text)  # создание цели
        self.tg_client.send_message(tg_user.chat_id, 'NewGoalCreated')  # сообщение пользователю
        self.clients.pop(tg_user.chat_id, None)  # удаление состояния пользователя

    """функция обработки сообщения неавторизованного пользователя"""
    def handle_unauthorized_user(self,  tg_user: TgUser, msg: Message) -> None:

        self.tg_client.send_message(tg_user.chat_id, 'Hello')  # сообщение приветствие пользователя
        tg_user.update_verification_code()  # генерация кода авторизации

        # отправка кода авторизации
        self.tg_client.send_message(tg_user.chat_id, f'You verification code:\n{tg_user.verification_code}')

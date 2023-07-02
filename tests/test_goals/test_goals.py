import pytest
from django.urls import reverse
from rest_framework import status

from goals.models import BoardParticipant, Goal
from rest_framework.fields import DateTimeField

from tests.test_goals.factories import CreateGoalRequest


@pytest.mark.django_db()
class TestCreateGoalView:
    url = reverse('goals:create_goal')

    def test_auth_required(self, client):
        response = client.post(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_failed_goal_create_for_not_participant(self, client, board, goal_category, faker, user):
        data = CreateGoalRequest.build(category=goal_category.id)
        client.force_login(user)
        response = client.post(self.url, data=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'mast be owner or writer role'}


    def test_failed_goal_create_for_reader(self, client, board, goal_category, board_participant, faker, user):

        board_participant.role = BoardParticipant.Role.reader
        board_participant.save()

        data = CreateGoalRequest.build(category=goal_category.id)
        client.force_login(user)
        response = client.post(self.url, data=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'mast be owner or writer role'}

    @pytest.mark.parametrize(
        'role',
        [BoardParticipant.Role.owner, BoardParticipant.Role.writer],
        ids=['owner', 'writer']
    )
    def test_goal_create_for_owner_or_writer(
            self, auth_client, board, goal_category, board_participant, faker, user, role
    ):

        board_participant.role = role
        board_participant.save(update_fields=['role'])

        data = CreateGoalRequest.build(category=goal_category.id)
        # client.force_login(user)
        response = auth_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_201_CREATED
        new_goal = Goal.objects.get()
        assert response.json() == _serialize_goal_create_response(new_goal)

    @pytest.mark.usefixtures('board_participant')
    def test_crete_goal_on_not_existing_category(self, auth_client):
        data = CreateGoalRequest.build(category=1)
        response = auth_client.post(self.url, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'category': ['Invalid pk "1" - object does not exist.']}


    @pytest.mark.usefixtures('board_participant')
    def test_crete_goal_on_deleted_category(self, auth_client, goal_category):
        goal_category.is_deleted = True
        goal_category.save(update_fields=['is_deleted'])
        data = CreateGoalRequest.build(category=goal_category.id)

        response = auth_client.post(self.url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {'category': ['Category not found']}






@pytest.mark.django_db()
class TestListGoalView:
    url = reverse('goals:list_goal')

    def test_goal_list_auth_required(self, client):
        response = client.get(self.url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_goal_list_for_owner_participant(self, auth_client, goal, user, board_participant):
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == _serialize_goal_list_response(Goal.objects.get())

    @pytest.mark.parametrize(
        'role',
        [BoardParticipant.Role.reader, BoardParticipant.Role.writer],
        ids=['reader', 'writer']
    )
    def test_goal_list_for_reader_or_writer_participant(self, auth_client, goal, user, board_participant, role):
        board_participant.role = role
        board_participant.save(update_fields=['role'])

        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == _serialize_goal_list_response(Goal.objects.get())

    def test_goal_list_for_not_participant(self, auth_client, goal, user):
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

@pytest.mark.django_db()
class TestDetailGoalView:
    # не работает так почему-то
    # @staticmethod
    # def get_goal_url(goal: Goal) -> str:
    #     return reverse('goals:detail_goal', kwargs={'pk', goal.pk})

    def test_goal_detail_for_not_participant(self, auth_client, goal, user):
        response = auth_client.get(f'/goals/goal/{goal.pk}')
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {'detail': 'You do not have permission to perform this action.'}

    def test_goal_detail_for_owner(self, auth_client, goal, user, board_participant):
        response = auth_client.get(f'/goals/goal/{goal.pk}')
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == _serialize_goal_list_response(Goal.objects.get())[0]

    @pytest.mark.parametrize(
        'role',
        [BoardParticipant.Role.reader, BoardParticipant.Role.writer],
        ids=['reader', 'writer']
    )
    def test_goal_detail_for_reader_or_writer(self, auth_client, goal, user, board_participant, role):
        board_participant.role = role
        response = auth_client.get(f'/goals/goal/{goal.pk}')
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == _serialize_goal_list_response(Goal.objects.get())[0]

    @pytest.mark.parametrize(
        'role',
        [BoardParticipant.Role.owner, BoardParticipant.Role.writer],
        ids=['owner', 'writer']
    )
    def test_goal_delete_for_owner_or_writer(self, auth_client, goal, user, board_participant, role):
        board_participant.role = role
        response = auth_client.delete(f'/goals/goal/{goal.pk}')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Goal.objects.get().status == Goal.Status.archived

    def test_goal_delete_for_reader(self, auth_client, goal, user, board_participant):
        board_participant.role = BoardParticipant.Role.reader
        board_participant.save()
        response = auth_client.delete(f'/goals/goal/{goal.pk}')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_goal_delete_for_not_participant(self, auth_client, goal, user):

        response = auth_client.delete(f'/goals/goal/{goal.pk}')
        assert response.status_code == status.HTTP_403_FORBIDDEN



def _serialize_goal_list_response(goal: Goal, **kwargs) -> list:
    data = [
        {'category': goal.category_id,
         'created': DateTimeField().to_representation(goal.created),
         'description': goal.description,
         'due_date': DateTimeField().to_representation(goal.due_date),
         'id': goal.id,
         'priority': goal.priority,
         'status': goal.status,
         'title': goal.title,
         'updated': DateTimeField().to_representation(goal.updated),
         'user': {'email': goal.user.email,
                  'first_name': goal.user.first_name,
                  'id': goal.user.id,
                  'last_name': goal.user.last_name,
                  'username': goal.user.username}}
    ]
    return data

def _serialize_goal_create_response(goal: Goal, **kwargs) -> dict:
    data = {
        'id': goal.id,
        'category': goal.category_id,
        'created': DateTimeField().to_representation(goal.created),
        'updated': DateTimeField().to_representation(goal.created),
        'title': goal.title,
        'description': goal.description,
        'due_date': DateTimeField().to_representation(goal.due_date),
        'status': goal.status,
        'priority': goal.priority
    }
    return data | kwargs
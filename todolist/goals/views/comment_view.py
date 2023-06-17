from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters,generics,permissions

from goals.serializers import GoalCommentCreateSerializer, GoalCommentDetailSerializer

from goals.models import GoalComment
from goals.permissions import GoalCommentPermission


class GoalCommentCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentCreateSerializer

class GoalCommentListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentDetailSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['goal']
    ordering = ['-created']

    def get_queryset(self):
        return GoalComment.objects.select_related('user').filter(user=self.request.user)

class GoalCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [GoalCommentPermission]
    serializer_class = GoalCommentDetailSerializer
    queryset = GoalComment.objects.select_related('user')





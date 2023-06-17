from django.urls import path

from goals.views import category_view, goal_view, comment_view


urlpatterns = [

    path("goal_category/create", category_view.GoalCategoryCreateView.as_view(), name='create_category'),
    path("goal_category/list", category_view.GoalCategoryListView.as_view(), name='list_category'),
    path("goal_category/<pk>", category_view.GoalCategoryView.as_view(), name='detail_category'),

    path("goal/create", goal_view.GoalCreateView.as_view(), name='create_goal'),
    path("goal/list", goal_view.GoalListView.as_view(), name='list_goal'),
    path("goal/<pk>", goal_view.GoalDetailView.as_view(), name='detail_goal'),

    path("goal_comment/create", comment_view.GoalCommentCreateView.as_view(), name='create_comment'),
    path("goal_comment/list", comment_view.GoalCommentListView.as_view(), name='list_comment'),
    path("goal_comment/<pk>", comment_view.GoalCommentDetailView.as_view(), name='detail_comment'),


]
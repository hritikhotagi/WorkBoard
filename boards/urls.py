from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, WorkBoardViewSet, TaskViewSet, get_user_by_id, get_tasks_by_status, get_users_by_task_board, get_task_count_by_board

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('boards', WorkBoardViewSet)
router.register('tasks', TaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('users/<int:user_id>/', get_user_by_id, name='get_user_by_id'),
    path('tasks/status/<int:board_id>/<str:status>/', get_tasks_by_status, name='tasks-by-status'),
    path('tasks/users/<int:board_id>/', get_users_by_task_board, name='users-by-task-board'),
    path('boards/<int:board_id>/task-count/', get_task_count_by_board, name='task-count-by-board'),
]

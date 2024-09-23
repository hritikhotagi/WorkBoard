from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import User, WorkBoard, Task
from .serializers import UserSerializer, TaskSerializer, WorkBoardSerializer
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# User View to register and fetch users
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(password=make_password(self.request.data.get('password')))

@api_view(['GET'])
def get_user_by_id(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=404)
    
# WorkBoard View
class WorkBoardViewSet(viewsets.ModelViewSet):
    queryset = WorkBoard.objects.all()
    serializer_class = WorkBoardSerializer
    permission_classes = [IsAuthenticated]  # Keep this as is for now

    def perform_create(self, serializer):
        # Save the workboard with the owner provided in the request
        owner_id = self.request.data.get('owner')
        try:
            owner = User.objects.get(id=owner_id)  # Fetch the user by id
        except User.DoesNotExist:
            return Response({"error": "Owner not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the workboard with the given owner (tasks will be handled by the serializer)
        serializer.save(owner=owner)

    def perform_update(self, serializer):
        # Allow updates, but ensure the user passed matches the owner
        owner_id = self.request.data.get('owner')
        try:
            owner = User.objects.get(id=owner_id)
        except User.DoesNotExist:
            return Response({"error": "Owner not found"}, status=status.HTTP_400_BAD_REQUEST)

        if self.get_object().owner != owner:
            return Response({"detail": "Only the owner can edit the board."}, status=status.HTTP_403_FORBIDDEN)

        serializer.save(owner=owner)



# Task View
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        work_board_id = self.request.data.get('work_board')
        if not work_board_id:
            return Response({"error": "work_board field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            work_board = WorkBoard.objects.get(id=work_board_id)
        except WorkBoard.DoesNotExist:
            return Response({"error": "Work board not found"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save(work_board=work_board)

    def update(self, request, *args, **kwargs):
        # Get the task instance to update
        instance = self.get_object()

        # Handle status update
        status = request.data.get("status")
        if status:
            if status not in dict(Task.STATUS_CHOICES).keys():
                return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
            instance.status = status

        # Handle assigned_to update if present in the request
        assigned_to_id = request.data.get("assigned_to")
        if assigned_to_id:
            try:
                assigned_to_user = User.objects.get(id=assigned_to_id)
                instance.assigned_to = assigned_to_user
            except User.DoesNotExist:
                return Response({"error": "Assigned user not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Save the changes
        instance.save()
        return Response(TaskSerializer(instance).data)


# Fetch tasks based on status for a specific workboard
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tasks_by_status(request, board_id, status):
    tasks = Task.objects.filter(work_board_id=board_id, status=status)
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


# Fetch users assigned to tasks in a workboard
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users_by_task_board(request, board_id):
    users = User.objects.filter(tasks__work_board_id=board_id).distinct()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


# Fetch task count in a workboard
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_task_count_by_board(request, board_id):
    count = Task.objects.filter(work_board_id=board_id).count()
    return Response({'task_count': count})

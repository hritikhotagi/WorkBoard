
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import User, WorkBoard, Task

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add additional user information to the response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'role': self.user.role,
        }
        
        return data
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']  # Added 'role'

class TaskSerializer(serializers.ModelSerializer):
    # Allow assigned_to to be writable and handle user object serialization
    assigned_to = UserSerializer(read_only=True)  # Read-only for serialization
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='assigned_to',  # This will set the assigned_to field to the related user object
        write_only=True,  # Write-only for task creation and updates
        required=False
    )
    work_board = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'assigned_to', 'assigned_to_id', 'work_board']

class WorkBoardSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, required=False)

    class Meta:
        model = WorkBoard
        fields = ['id', 'title', 'description', 'owner', 'tasks']

    def create(self, validated_data):
        tasks_data = validated_data.pop('tasks', [])
        workboard = WorkBoard.objects.create(**validated_data)

        for task_data in tasks_data:
            assigned_to_id = task_data.pop('assigned_to_id', None)
            task = Task.objects.create(work_board=workboard, **task_data)
            if assigned_to_id:
                task.assigned_to = assigned_to_id
                task.save()

        return workboard

    def update(self, instance, validated_data):
        tasks_data = validated_data.pop('tasks', [])
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        for task_data in tasks_data:
            task_id = task_data.get('id')
            if task_id:
                # Update existing tasks
                task = Task.objects.get(id=task_id, work_board=instance)
                task.title = task_data.get('title', task.title)
                task.description = task_data.get('description', task.description)
                task.status = task_data.get('status', task.status)
                assigned_to_id = task_data.get('assigned_to_id')
                if assigned_to_id:
                    task.assigned_to_id = assigned_to_id
                task.save()
            else:
                # Create new tasks
                Task.objects.create(work_board=instance, **task_data)

        return instance
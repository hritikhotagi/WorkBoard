from django.contrib.auth.models import AbstractUser
from django.db import models

# Custom User model to handle roles
class User(AbstractUser):
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('collaborator', 'Collaborator'),
        ('viewer', 'Viewer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='owner')

    # Adding related_name arguments to avoid clashes with the default auth.User model
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='boards_user_set',  # Custom related_name
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='boards_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.username


class WorkBoard(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="boards")

    def __str__(self):
        return self.title

class Task(models.Model):
    STATUS_CHOICES = (
        ('todo', 'To-Do'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="tasks")
    work_board = models.ForeignKey(WorkBoard, on_delete=models.CASCADE, related_name="tasks")

    def __str__(self):
        return self.title
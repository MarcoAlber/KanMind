from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Board(models.Model):
    """
    Represents a Kanban board.
    
    Attributes:
        title (str): Title of the board.
        owner (User): The user who owns the board.
        members (User list): Users who are members of the board.
        created_at (date): Date when the board was created.
    """
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_boards')
    members = models.ManyToManyField(User, related_name='boards')
    created_at = models.DateField(auto_now_add=True)


class Task(models.Model):
    """
    Represents a task within a board.
    
    Attributes:
        board (Board): Board this task belongs to.
        title (str): Title of the task.
        description (str): Optional detailed description of the task.
        status (str): Task status ('to-do', 'in-progress', 'review', 'done').
        priority (str): Task priority ('low', 'medium', 'high').
        assignee (User): User assigned to complete the task.
        reviewer (User): User responsible for reviewing the task.
        due_date (date): Optional due date.
        created_at (datetime): Timestamp when the task was created.
        created_by (User): User who created the task.
    """
    STATUS_CHOICES = [
        ('to-do', 'To Do'),
        ('in-progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='review_tasks')
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')


class Comment(models.Model):
    """
    Represents a comment on a task.
    
    Attributes:
        task (Task): The task this comment belongs to.
        author (User): User who wrote the comment.
        content (str): Comment content.
        created_at (datetime): Timestamp when the comment was created.
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
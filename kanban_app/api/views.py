from rest_framework.permissions import IsAuthenticated
from kanban_app.models import Board, Task, Comment
from kanban_app.api.permissions import IsTaskBoardMemberOrOwner, IsBoardMemberOrOwner, IsCommentAuthor
from django.db.models import Q, Count
from rest_framework.response import Response
from .serializers import BoardSerializer, BoardDetailSerializer, BoardUpdateSerializer, TaskSerializer, CommentSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

class BoardViewSet(ModelViewSet):
    """
    API endpoint for managing boards.
    Only accessible by board members or owners.
    """
    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]

    def get_queryset(self):
        """
        Return boards where the user is either the owner or a member for listing,
        otherwise return all boards.
        """
        user = self.request.user
        action = self.action

        if action == 'list':
            return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
        else:
            return Board.objects.all()
    
    def get_serializer_class(self):
        """
        Select serializer class based on the action.
        """
        if self.action == 'list' or self.action == 'create':
            return BoardSerializer
        elif self.action in ['update', 'partial_update']:
            return BoardUpdateSerializer
        return BoardDetailSerializer

class TaskViewSet(ModelViewSet):
    """
    API endpoint for managing tasks.
    Only accessible by task board members or owners.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMemberOrOwner]

    def list(self, request, *args, **kwargs):
        """
        Disable listing all tasks.
        """
        return Response({"detail": "Listing all Tasks is not allowed"}, status = 405)


    def destroy(self, request, *args, **kwargs):
        """
        Delete a task after checking object permissions.
        """
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='assigned-to-me')
    def assigned(self, request):
        """
        Return tasks assigned to the current user with comment counts.
        """
        tasks = Task.objects.filter(assignee=request.user).annotate(comments_count=Count('comments'))

        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes = [IsAuthenticated], url_path='reviewing')
    def reviewed(self, request):
        """
        Return tasks where the current user is the reviewer, including comment counts.
        """
        tasks = Task.objects.filter(reviewer=request.user).annotate(comments_count=Count('comments'))

        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    

class TaskCommentViewSet(ModelViewSet):
    """
    API endpoint for managing comments on tasks.
    Permissions differ depending on action.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        """
        Return comments for a specific task.
        """
        task_id = self.kwargs.get('task_pk')
        return Comment.objects.filter(task_id=task_id)
    
    def perform_create(self, serializer):
        """
        Create a comment for a specific task and set the author as the current user.
        """
        task_id = self.kwargs.get('task_pk')
        task = get_object_or_404(Task, id=task_id)
        serializer.save(task=task, author=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a comment after checking object permissions.
        """
        instance = self.get_object()
        self.check_object_permissions(request, instance) 
        return super().destroy(request, *args, **kwargs)

    def get_permissions(self):
        """
        Return different permissions depending on the action:
        - destroy: only comment author can delete
        - others: task board members or owners
        """
        if self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsCommentAuthor]
        else:
            permission_classes = [IsAuthenticated, IsTaskBoardMemberOrOwner]
        return [permission() for permission in permission_classes]

    def get_object(self):
        """
        Retrieve a comment object by task and comment IDs.
        """
        task_id = self.kwargs.get('task_pk')
        comment_id = self.kwargs.get('pk')
        obj = get_object_or_404(Comment, id=comment_id, task_id=task_id)
        return obj
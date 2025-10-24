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
    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated, IsBoardMemberOrOwner]

    def get_queryset(self):
        user = self.request.user
        action = self.action

        if action == 'list':
            return Board.objects.filter(Q(owner=user) | Q(members=user)).distinct()
        else:
            return Board.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'create':
            return BoardSerializer
        elif self.action in ['update', 'partial_update']:
            return BoardUpdateSerializer
        return BoardDetailSerializer

class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsTaskBoardMemberOrOwner]

    def list(self, request, *args, **kwargs):
        return Response({"detail": "Listing all Tasks is not allowed"}, status = 405)


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='assigned-to-me')
    def assigned(self, request):
        tasks = Task.objects.filter(assignee=request.user).annotate(comments_count=Count('comments'))

        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes = [IsAuthenticated], url_path='reviewing')
    def reviewed(self, request):
        tasks = Task.objects.filter(reviewer=request.user).annotate(comments_count=Count('comments'))

        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    

class TaskCommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        task_id = self.kwargs.get('task_pk')
        return Comment.objects.filter(task_id=task_id)
    
    def perform_create(self, serializer):
        task_id = self.kwargs.get('task_pk')
        task = get_object_or_404(Task, id=task_id)
        serializer.save(task=task, author=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance) 
        return super().destroy(request, *args, **kwargs)

    def get_permissions(self):
        if self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsCommentAuthor]
        else:
            permission_classes = [IsAuthenticated, IsTaskBoardMemberOrOwner]
        return [permission() for permission in permission_classes]

    def get_object(self):
        task_id = self.kwargs.get('task_pk')
        comment_id = self.kwargs.get('pk')
        obj = get_object_or_404(Comment, id=comment_id, task_id=task_id)
        return obj
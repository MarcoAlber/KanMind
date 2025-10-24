from rest_framework.permissions import BasePermission
from kanban_app.models import Board, Task


class IsTaskBoardMemberOrOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        board = obj.board

        if request.method == 'DELETE':
            return (
                board.owner == request.user or
                obj.created_by == request.user
            )

        return (
            board.owner == request.user or
            board.members.filter(id=request.user.id).exists()
        )

    def has_permission(self, request, view):
        if request.method == "POST":
            board_id = request.data.get('board')
            if board_id:
                try:
                    board = Board.objects.get(id=board_id)
                except Board.DoesNotExist:
                    return False
            else:
                task_id = view.kwargs.get('task_pk')
                if not task_id:
                    return False
                try: 
                    task = Task.objects.get(id=task_id)
                    board = task.board
                except Task.DoesNotExist:
                    return False

            return (
                board.owner == request.user or
                board.members.filter(id=request.user.id).exists()
            )
        
        task_id = view.kwargs.get('pk') or view.kwargs.get('task_pk')
        if not task_id:
            return False

        try:
            task = Task.objects.get(id=task_id)
            board = task.board
        except Task.DoesNotExist:
            return False

        return (
            board.owner == request.user or
            board.members.filter(id=request.user.id).exists()
        )

class IsBoardMemberOrOwner(BasePermission):
    def has_object_permission(self, request, view, obj):

        if request.method == 'DELETE':
            return obj.owner == request.user

        return (
            obj.owner == request.user or
            obj.members.filter(id=request.user.id).exists()
        )

    def has_permission(self, request, view):
        return request.user.is_authenticated

class IsCommentAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
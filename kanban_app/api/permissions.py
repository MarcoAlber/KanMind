from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotFound
from kanban_app.models import Board, Task


class IsTaskBoardMemberOrOwner(BasePermission):
    """
    Permission to allow actions on a Task only if the user is:
    - the owner of the board, or
    - a member of the board.
    
    DELETE requests additionally allow the creator of the task.
    """

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission for a Task instance.
        Allows DELETE only to task creator or board owner.
        Other methods allowed for board owner or members.
        """
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
        """
        Check if the user can access or create a task.

        POST: verify board exists and user is owner or member.
        Other methods: verify task exists and user is board owner or member.

        Raises NotFound if the board or task does not exist.
        Returns True if permission is granted, False otherwise.
        """
        if request.method == "POST":
            board_id = request.data.get('board')
            if board_id:
                try:
                    board = Board.objects.get(id=board_id)
                except Board.DoesNotExist:
                    raise NotFound("Board not found.")
            else:
                task_id = view.kwargs.get('task_pk')
                if not task_id:
                    return False
                try: 
                    task = Task.objects.get(id=task_id)
                    board = task.board
                except Task.DoesNotExist:
                    raise NotFound("Task not found.")

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
            raise NotFound("Task not found.")

        return (
            board.owner == request.user or
            board.members.filter(id=request.user.id).exists()
        )

class IsBoardMemberOrOwner(BasePermission):
    """
    Permission to allow actions on a Board only if the user is:
    - the board owner, or
    - a member of the board.

    DELETE requests are allowed only for the owner.
    """
    def has_object_permission(self, request, view, obj):
        """Object-level permission for Board instance."""

        if request.method == 'DELETE':
            return obj.owner == request.user

        return (
            obj.owner == request.user or
            obj.members.filter(id=request.user.id).exists()
        )

    def has_permission(self, request, view):
        """General permission: user must be authenticated."""
        return request.user.is_authenticated

class IsCommentAuthor(BasePermission):
    """
    Permission to allow only the author of a comment to modify or delete it.
    """
    def has_object_permission(self, request, view, obj):
        """Object-level permission for Comment instance."""
        return obj.author == request.user
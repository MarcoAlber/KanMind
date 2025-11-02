from django.contrib import admin
from .models import Board, Task, Comment

class TaskInline(admin.TabularInline):
    """
    Inline admin for displaying Tasks within a Board.
    """
    model = Task
    extra = 1
    fields = ('title', 'status', 'priority', 'assignee', 'reviewer', 'due_date')
    readonly_fields = ('created_by',)
    show_change_link = True

    def save_model(self, request, obj, form, change):
        """
        Automatically set the creator when a Task is created via inline.
        """
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class CommentInline(admin.TabularInline):
    """
    Inline admin for displaying Comments within a Task.
    """
    model = Comment
    extra = 1
    fields = ('author', 'content', 'created_at')
    readonly_fields = ('author', 'created_at')
    show_change_link = True

    def save_model(self, request, obj, form, change):
        """
        Automatically set the author when a Comment is created via inline.
        """
        if not obj.pk:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """
    Admin interface for Boards.

    Displays board summary including member count, total tasks,
    tasks to do, and high priority tasks.
    """
    list_display = (
        'id', 'title', 'owner', 'member_count',
        'ticket_count', 'tasks_to_do_count', 'tasks_high_prio_count'
    )
    search_fields = ('title', 'owner__username', 'owner__email')
    list_filter = ('owner',)
    filter_horizontal = ('members',)
    inlines = [TaskInline]
    ordering = ('-id',)
    readonly_fields = ('created_at',)

    def member_count(self, obj):
        """Return number of members in the board."""
        return obj.members.count()
    member_count.short_description = "Mitglieder"

    def ticket_count(self, obj):
        """Return total number of tasks in the board."""
        return obj.tasks.count()
    ticket_count.short_description = "Anzahl Tasks"

    def tasks_to_do_count(self, obj):
        """Return number of tasks with status 'to-do'."""
        return obj.tasks.filter(status='to-do').count()
    tasks_to_do_count.short_description = "To-Do Tasks"

    def tasks_high_prio_count(self, obj):
        """Return number of tasks with high priority."""
        return obj.tasks.filter(priority='high').count()
    tasks_high_prio_count.short_description = "High Priority Tasks"


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Admin interface for Tasks.

    Displays task details, assignee, reviewer, status, priority, due date,
    and total comments.
    """
    list_display = (
        'id', 'title', 'board', 'assignee', 'reviewer',
        'status', 'priority', 'due_date', 'comments_count'
    )
    search_fields = (
        'title', 'description', 'assignee__username',
        'reviewer__username', 'board__title'
    )
    list_filter = ('board', 'status', 'priority')
    raw_id_fields = ('assignee', 'reviewer', 'board', 'created_by')
    inlines = [CommentInline]
    ordering = ('-id',)
    readonly_fields = ('created_at',)

    def comments_count(self, obj):
        """Return total number of comments on the task."""
        return obj.comments.count()
    comments_count.short_description = "Kommentare"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface for Comments.

    Displays comment details including task, author, creation time, and content.
    """
    list_display = ('id', 'task', 'author', 'created_at', 'short_content')
    search_fields = ('content', 'author__username', 'task__title')
    list_filter = ('task', 'author')
    readonly_fields = ('author', 'created_at')
    ordering = ('-id',)

    def short_content(self, obj):
        """Show only a short preview of comment content."""
        return (obj.content[:50] + '...') if len(obj.content) > 50 else obj.content
    short_content.short_description = "Kommentarvorschau"

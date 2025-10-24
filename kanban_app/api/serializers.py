from rest_framework import serializers
from ..models import Board, Task, Comment
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']
    
    def get_fullname(self, obj):
        fullname = obj.first_name + " " + obj.last_name
        return fullname

class TaskSerializer(serializers.ModelSerializer):
    board = serializers.PrimaryKeyRelatedField(queryset=Board.objects.all(), required=False)
    assignee_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    reviewer_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    assignee = UserSerializer(read_only=True)
    reviewer = UserSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'assignee_id', 'reviewer_id', 'assignee', 'reviewer',
            'due_date', 'comments_count'
        ]
        read_only_fields = ['id', 'assignee', 'reviewer', 'comments_count']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.method == 'PATCH':
            data.pop('board', None)
            data.pop('comments_count', None)

        return data
    
    def validate(self, data):
        request_user = self.context['request'].user
        method = self.context['request'].method
        board = data.get('board')

        if method == 'POST':
            board = data.get('board')
            if not board:
                raise serializers.ValidationError("board_id is required")
        
        else:
            if 'board' in data:
                raise serializers.ValidationError("Changing board is not allowed")
        
            board = self.instance.board if self.instance else None


        if board and not board.members.filter(id=request_user.id).exists():
            raise serializers.ValidationError("Not a member of the board")

        assignee_id = data.get('assignee_id')
        reviewer_id = data.get('reviewer_id')

        if assignee_id and not board.members.filter(id=assignee_id).exists():
            raise serializers.ValidationError("Assignee is not a member of the board")
    
        if reviewer_id and not board.members.filter(id=reviewer_id).exists():
            raise serializers.ValidationError("Reviewer is not a member of the board")

        data['board'] = board

        return data
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def create(self, validated_data):
        request_user = self.context['request'].user
        assignee_id = validated_data.pop('assignee_id', None)
        reviewer_id = validated_data.pop('reviewer_id', None)
        board = validated_data.pop('board')

        assignee = User.objects.get(id=assignee_id) if assignee_id else None
        reviewer = User.objects.get(id=reviewer_id) if reviewer_id else None

        task = Task.objects.create(board=board, assignee=assignee, reviewer=reviewer, created_by=request_user,  **validated_data)
        return task

class BoardSerializer(serializers.ModelSerializer):
    members = serializers.ListField( 
        child=serializers.IntegerField(),
        write_only=True)
    
    member_count = serializers.SerializerMethodField(read_only=True)
    ticket_count = serializers.SerializerMethodField(read_only=True)
    tasks_to_do_count = serializers.SerializerMethodField(read_only=True)
    tasks_high_prio_count = serializers.SerializerMethodField(read_only=True)
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'members',
            'member_count', 'ticket_count',
            'tasks_to_do_count', 'tasks_high_prio_count', 'owner_id'
        ]

    def validate(self, data):
        members_ids = data.get('members', [])
        users = User.objects.filter(id__in=members_ids)
        if len(users) != len(set(members_ids)):
            raise serializers.ValidationError("Ein oder mehrere Benutzer existieren nicht")
        return data

    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_ticket_count(self, obj):
        return obj.tasks.count()
    
    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status='to-do').count()
    
    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority='high').count()

    def create(self, validated_data):
        members_ids = validated_data.pop('members')
        owner = self.context['request'].user
        if owner.id not in members_ids:
            members_ids.append(owner.id)
        users = User.objects.filter(id__in=members_ids)
        board = Board.objects.create(title=validated_data['title'], owner=owner)
        board.members.set(users)
        return board

class BoardDetailSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = [
            'id', 'title', 'owner_id', 'members', 'tasks'
        ]

class BoardUpdateSerializer(serializers.ModelSerializer):
    members = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    owner_data = UserSerializer(source='owner', read_only=True)
    members_data = UserSerializer(source='members', many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'owner_data', 'members_data']

    def validate_members(self, value):
        owner_id = self.instance.owner.id if self.instance else None
        if owner_id and owner_id not in value:
            value.append(owner_id)

        users = User.objects.filter(id__in=value)
        if len(users) != len(set(value)):
            raise serializers.ValidationError("Ein oder mehrere Benutzer Ids sind ungültig")

        current_member_ids = set(self.instance.members.values_list('id', flat=True))
        new_members_ids = set(value)
        removed_ids = current_member_ids - new_members_ids

        board_tasks  = self.instance.tasks.all()

        blocked_users = set()
        for task in board_tasks:
            if task.assignee_id in removed_ids or task.reviewer_id in removed_ids:
                blocked_users.add(task.assignee_id)
                blocked_users.add(task.reviewer_id)
        
        blocked_users.discard(None)

        if blocked_users:
            raise serializers.ValidationError(f"Folgende Benutzer können nicht entfernt werden, da sie mit Aufgaben verknüoft sind: {list(blocked_users)}")

        return value
    
    def update(self, instance, validated_data):
        members_ids = validated_data.get('members', None)

        instance.title = validated_data.get('title', instance.title)
        instance.save()
        if members_ids is not None:
            users = User.objects.filter(id__in=members_ids)
            instance.members.set(users)

        return instance


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'created_at', 'author', 'content']
        read_only_fields = ['id', 'created_at', 'author']

    def get_author(self, obj):
        return f"{obj.author.first_name} {obj.author.last_name}".strip()
    
    def create(self, validated_data):
        request = self.context['request']
        validated_data['author'] = request.user
        return super().create(validated_data)
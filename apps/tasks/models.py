from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.models import CustomBaseModel


User = settings.AUTH_USER_MODEL

class Priority(models.Model):
    """Model to define task priority."""
    name = models.CharField(max_length=20)
    # using a simple char field, no need for complicated relations.
    color = models.CharField(max_length=20, default="#FFFFFF")
    # can use order to sort the data instead of random order.
    order = models.IntegerField(default=0)
    weightage = models.IntegerField(default=0, help_text="Priority Weightage, use this to define priority, higher weightage means higher priority.", )


    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
        verbose_name = "Priority"
        verbose_name_plural = "Priorities"
        permissions = [("manage_priorities", "Can create, edit, delete priorities")]


class Group(CustomBaseModel):
    """
    class to save groups, a group can be used as a collection to tasks,
    Example: sprint 1, sprint 2, sprint 3, etc. so it can be used to track tasks in a sprint.
    only members have access to the group and tasks under that group.
    """
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name="task_groups")

    class Meta:
        permissions = [("manage_groups", "Can create, Can edit, Can delete groups")]

    def __str__(self):
        return self.name


class Tasks(CustomBaseModel):
    """
    class to define tasks.
    only assigned people have access to tasks,
    so we will filter tasks based on group members.
    """
    class Status(models.TextChoices):
        TODO = 'TODO', 'To Do'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        DONE = 'DONE', 'Done'

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="tasks")
    priority = models.ForeignKey(Priority, on_delete=models.PROTECT, related_name="tasks")
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    estimated_time = models.IntegerField(help_text="Estimated time in seconds")

    locked_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        permissions = [("manage_tasks", "Can create, Can edit, Can delete tasks")]
        # minimizing index usage to balance between read and write speed.
        # adding index for group, priority and status for faster query.
        indexes = [models.Index(
            fields=[
                "group",
                "priority",
                "status",
            ],
        )]

    def __str__(self):
        return self.title

    @property
    def is_locked(self):
        """Helper to quickly check if the task is currently in a lockdown period."""
        if self.locked_until:
            return self.locked_until > timezone.now()
        return False
    
    
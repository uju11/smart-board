import time
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.cache import cache
from .models import Tasks, Group, Priority
from .messages import CrypticMessages

User = get_user_model()

# --- Common Services ---
def list_priorities_service():
    return Priority.objects.all()

def list_statuses_service():
    return [{"id": choice.value, "name": choice.label} for choice in Tasks.Status]

def list_all_users_service():
    return User.objects.all()

# --- Group Services ---
def list_user_groups_service(user):
    if user.is_staff:
        return Group.objects.prefetch_related('members').all()
    return Group.objects.prefetch_related('members').filter(members=user)

def list_all_groups_service():
    return Group.objects.prefetch_related('members').all()

def create_group_service(name: str, creator, member_ids: list[int] = None) -> Group:
    group = Group.objects.create(name=name)
    
    # Automatically add the creator as a member
    members_to_add = set([creator.id])
    if member_ids:
        members_to_add.update(member_ids)
        
    group.members.set(members_to_add)
    return group

def delete_group_service(group_id: int):
    group = get_object_or_404(Group, id=group_id)
    
    if Tasks.objects.filter(group=group).exists():
        return False, CrypticMessages.MEMBER_HAS_TASKS
        
    group.delete()
    return True, CrypticMessages.GROUP_DELETED

def update_group_service(group_id: int, name: str = None, new_member_ids: list[int] = None):
    """
    Handles updating a group's name and/or members. 
    Includes validation to prevent removing members with active tasks.
    """
    group = get_object_or_404(Group, id=group_id)
    
    # 1. Update Name (if provided)
    if name is not None:
        group.name = name
        group.save()

    # 2. Update Members (if provided)
    if new_member_ids is not None:
        current_member_ids = set(group.members.values_list('id', flat=True))
        new_member_ids_set = set(new_member_ids)
        
        # Validation: Find who is being removed
        removed_member_ids = current_member_ids - new_member_ids_set
        
        if removed_member_ids:
            has_active_tasks = Tasks.objects.filter(
                group=group, 
                assignee_id__in=removed_member_ids
            ).exists()
            
            if has_active_tasks:
                return False, CrypticMessages.MEMBER_HAS_TASKS
                
        # If validation passes, update the members
        group.members.set(new_member_ids_set)
        
    return True, group


# --- Task Services ---

def list_tasks_by_group_service(group_id: int, user):
    """
    Fetches tasks for a specific group, ensuring the user 
    is either an admin or a member of that group.
    """
    group = get_object_or_404(Group, id=group_id)
    
    # Security: If they aren't staff AND aren't in the group's member list, block them.
    if not user.is_staff and not group.members.filter(id=user.id).exists():
        return None 
        
    return Tasks.objects.filter(group=group)    

def create_task_service(title: str, group_id: int, priority_id: int, estimated_time: int, assignee_id: int, should_lock: bool) -> Tasks:
    """Handles the creation of a task with business validation."""
    group = get_object_or_404(Group, id=group_id)

    task = Tasks.objects.create(
        title=title,
        group=group,
        priority_id=priority_id,
        estimated_time=estimated_time,
        assigned_to_id=assignee_id
    )

    task.estimated_time = override_estimated_time(task)

    if should_lock:
        task.locked_until = timezone.now() + timedelta(minutes=5)
        
    task.save()
    
    return task

def update_task_service(task_id: int, title: str, group_id: int, priority_id: int, estimated_time: int, assignee_id: int, status: str) -> Tasks:
    """Handles updating a task."""
    task = get_object_or_404(Tasks, id=task_id)
    
    if task.is_locked:
        return False, CrypticMessages.LOCKED_TASK_EDIT

    if status == 'DONE' and task.status != 'DONE':

        # Calculate exactly how long this task has been alive
        time_alive = timezone.now() - task.created_at
        
        if time_alive.total_seconds() < 60:
            seconds_left = int(60 - time_alive.total_seconds())
            return False, CrypticMessages.TOO_FAST_CLOSE.format(seconds=seconds_left)

        # Is the task they are trying to close a High or Medium priority?
        # (If it's already a Low priority task, we let them close it, otherwise they could never start!)
        if task.priority.name.lower() != 'low':
            
            # Check if this specific user has ANY completed low-priority tasks in THIS specific group
            has_completed_low_task = Tasks.objects.filter(
                group_id=group_id,
                assigned_to_id=assignee_id,
                priority__name__iexact='low',
                status='DONE'
            ).exists()
            
            if not has_completed_low_task:
                return False, CrypticMessages.PREREQUISITE_BLOCKED

    task.title = title
    task.group_id = group_id
    task.priority_id = priority_id
    task.estimated_time = estimated_time
    task.assigned_to_id = assignee_id
    task.status = status
    task.save()
    return True, task

def delete_task_service(task_id: int):
    """Encapsulates the deletion logic."""
    task = get_object_or_404(Tasks, id=task_id)

    if task.is_locked:
        return False, CrypticMessages.LOCKED_TASK_DELETE
    
    task.delete()
    return True, CrypticMessages.TASK_DELETED

def check_if_a_task_should_lock(user_id: int) -> bool:
    """
    check and updates if the new task should be locked.
    """
    history_key = f"task_history_{user_id}"
    now = time.time()
    history = cache.get(history_key, [])
    recent_history = [timestamp for timestamp in history if now - timestamp < 120]

    # check if it is 4th task or higher.
    should_lock = len(recent_history) >= 3

    recent_history.append(now)
    cache.set(history_key, recent_history, timeout=120)

    return should_lock

def limit_task_creation(user_id:int) -> tuple[bool, str]:
    """
    requirement 1:
    checks if a user created 3 tasks within 2minutes, if so locks the 4th task
    for 5 minutes, unlocks after 5+1 minutes.

    """
    lock_key = f"task_lock_{user_id}"
    history_key = f"task_history_{user_id}"

    # check if they are currently locked out.
    if cache.get(lock_key):
        return False, CrypticMessages.RATE_LIMIT_EXCEEDED

    # fetch the users recent activity
    now = time.time()
    history = cache.get(history_key, [])

    recent_history = [timestamp for timestamp in history if now - timestamp < 120]

    if len(recent_history) >= 3:
        cache.set(lock_key, "locked", timeout=300)
        return False, CrypticMessages.RATE_LIMIT_EXCEEDED

    # if safe, record this attempt.
    recent_history.append(now)
    # set timeout to 2mins, only need to remember for 2mins.
    cache.set(history_key, recent_history, timeout=120)
    return True, ""

# hidden logic.
def override_estimated_time(task: Tasks) -> int:
    """
    logic: if the task created time is an even number, keep the estimated time as it is,
    else keep the estimated time to 60 minutes.
    """
    if not task.created_at:
        return task.estimated_time
        
    created_time_minute = task.created_at.minute
    
    if created_time_minute % 2 == 0:
        return task.estimated_time
    else:
        return 3600  # 60 minutes in seconds

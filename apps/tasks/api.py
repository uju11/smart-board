"""
careful with the endoints, if similar endoints exist,
might cause a conflict in future, try to keep it unique.
"""

from ninja import Router
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth
from typing import List
from .schemas import GroupSchema, TaskCreateSchema, TaskUpdateSchema, TaskResponseSchema, TaskCreateResponseSchema, PrioritySchema, StatusSchema, UserSchema, GroupUpdateSchema, GroupCreateSchema
from .services import (
    list_user_groups_service,
    list_all_groups_service,
    create_group_service,
    delete_group_service,
    update_group_service,
    create_task_service,
    update_task_service,
    delete_task_service,
    list_tasks_by_group_service,
    list_priorities_service,
    list_statuses_service,
    list_all_users_service,
    check_if_a_task_should_lock,
    override_estimated_time
)
from .messages import CrypticMessages

router = Router(auth=JWTAuth())

# common endpoints
@router.get("/priorities", response=List[PrioritySchema])
def list_priorities(request):
    return list_priorities_service()

@router.get("/users", response=List[UserSchema])
def list_users(request):
    return list_all_users_service()

@router.get("/users/me", response=UserSchema)
def get_current_user(request):
    return request.user

@router.get("/statuses", response=List[StatusSchema])
def list_statuses(request):
    return list_statuses_service()

# group endpoints
@router.get("/groups", response=List[GroupSchema])
def list_groups(request):
    """Returns a list of groups the authenticated user is a member of."""
    return list_user_groups_service(request.user)

@router.get("/groups/all", response=List[GroupSchema])
def list_all_groups(request):
    """Returns all groups in the system (Admin only)."""
    if not request.user.is_staff:
        raise HttpError(403, CrypticMessages.UNAUTHORIZED)
    return list_all_groups_service()

@router.post("/groups", response=GroupSchema)
def create_group(request, data: GroupCreateSchema):
    # Enforce Admin Permission
    if not request.user.is_staff:
        raise HttpError(403, CrypticMessages.UNAUTHORIZED)
    
    return create_group_service(data.name, request.user, data.member_ids)

@router.delete("/groups/{group_id}", response={200: dict})
def delete_group(request, group_id: int):
    if not request.user.is_staff:
        raise HttpError(403, CrypticMessages.UNAUTHORIZED)
        
    success, result = delete_group_service(group_id)
    if not success:
        raise HttpError(423, result)
        
    return {"message": result}

@router.put("/groups/{group_id}", response=GroupSchema)
def update_group(request, group_id: int, data: GroupUpdateSchema):
    """Updates a group's name, members, or both (Admin only)."""
    
    if not request.user.is_staff:
        raise HttpError(403, CrypticMessages.UNAUTHORIZED)
        
    # Pass the optional data directly to the service
    success, result = update_group_service(
        group_id=group_id, 
        name=data.name, 
        new_member_ids=data.member_ids
    )
    
    # Handle the validation error
    if not success:
        raise HttpError(400, result)
        
    return result


# task endpoints
@router.post("/tasks", response=TaskCreateResponseSchema)
def create_task(request, data: TaskCreateSchema):
    if not request.user.is_staff:
        raise HttpError(403, CrypticMessages.UNAUTHORIZED)

    ## 1. Ask Redis if this task needs to be locked
    should_lock = check_if_a_task_should_lock(request.user.id)

    # The API just calls the service and returns the result
    task = create_task_service(
        title=data.title,
        group_id=data.group_id,
        priority_id=data.priority_id,
        estimated_time=data.estimated_time,
        assignee_id=data.assignee_id,
        should_lock=should_lock
    )
    return {"message": CrypticMessages.TASK_CREATED, "task": task}

@router.put("/tasks/{task_id}", response=TaskCreateResponseSchema)
def update_task(request, task_id: int, data: TaskUpdateSchema):
    if not request.user.is_staff:
        raise HttpError(403, CrypticMessages.UNAUTHORIZED)
        
    success, result = update_task_service(
        task_id=task_id,
        title=data.title,
        group_id=data.group_id,
        priority_id=data.priority_id,
        estimated_time=data.estimated_time,
        assignee_id=data.assignee_id,
        status=data.status
    )
    if not success:
        raise HttpError(423, result)
    
    return {"message": CrypticMessages.TASK_UPDATED, "task": result}

@router.delete("/tasks/{task_id}", response={200: dict})
def delete_task(request, task_id: int):
    if not request.user.is_staff:
        raise HttpError(403, CrypticMessages.UNAUTHORIZED)
        
    success, result = delete_task_service(task_id)
    if not success:
        raise HttpError(423, result)
    
    return {"message": result}

@router.get("/groups/{group_id}/tasks", response=List[TaskResponseSchema])
def list_group_tasks(request, group_id: int):
    """Returns all tasks belonging to a specific group."""
    tasks = list_tasks_by_group_service(group_id, request.user)
    if tasks is None:
        raise HttpError(403, "Unauthorized")
    return tasks

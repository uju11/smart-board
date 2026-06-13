from ninja import Schema
from typing import List, Optional


class UserSchema(Schema):
    id: int
    username: str

class GroupSchema(Schema):
    id: int
    name: str
    members: List[UserSchema] = []

class GroupCreateSchema(Schema):
    name: str
    member_ids: Optional[List[int]] = None

class TaskCreateSchema(Schema):
    title: str
    group_id: int
    priority_id: int
    estimated_time: int
    assignee_id: int

class TaskUpdateSchema(TaskCreateSchema):
    status: str

class StatusSchema(Schema):
    id: str
    name: str

class PrioritySchema(Schema):
    id: int
    name: str
    color: str
    order: int
    weightage: int

class GroupUpdateSchema(Schema):
    """Schema for updating a group. Fields are optional to allow partial updates."""
    name: Optional[str] = None
    member_ids: Optional[List[int]] = None

from datetime import datetime

class TaskResponseSchema(Schema):
    id: int
    title: str
    status: str
    is_locked: bool
    locked_until: Optional[datetime] = None
    estimated_time: int
    priority_id: int
    assigned_to_id: Optional[int] = None

class TaskCreateResponseSchema(Schema):
    message: str
    task: TaskResponseSchema
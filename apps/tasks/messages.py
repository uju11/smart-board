"""
This file contains the messages that will be displayed to the user.
"""

class CrypticMessages:
    # --- Authentication & Permissions ---
    UNAUTHORIZED = "You speak to doors that do not know your name."
    
    # --- Rate Limiting & Locks ---
    RATE_LIMIT_EXCEEDED = "The weaver's loom is jammed. The thread is locked for 5 minutes."
    LOCKED_TASK_EDIT = "What is bound by time cannot be reshaped by force."
    LOCKED_TASK_DELETE = "The void refuses your offering. The seal holds."
    
    # --- Business Rules ---
    TOO_FAST_CLOSE = "The ink is still wet. The scroll must breathe for {seconds} more seconds."
    PREREQUISITE_BLOCKED = "The roof cannot precede the foundation. Seek the lower paths first."
    MEMBER_HAS_TASKS = "Burdens must be reassigned before the bearer departs the circle."
    
    # --- Success Messages ---
    TASK_CREATED = "A new thread is woven into the tapestry."
    TASK_UPDATED = "The threads have been re-woven."
    TASK_DELETED = "A whisper into the void, successfully forgotten."
    GROUP_DELETED = "The gathering is scattered to the winds."

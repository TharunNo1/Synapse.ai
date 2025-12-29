from pydantic import BaseModel, Field
from typing import Optional

class TaskStatus(BaseModel):
    task_id: str
    status: str
    download_url: Optional[str] = None
    error: Optional[str] = None
from pydantic import BaseModel,Field,ConfigDict
from fastapi import WebSocket
from uuid import uuid4
from datetime import datetime,timezone

class ConnectionModel(BaseModel):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    id:str = Field(default_factory=lambda:str(uuid4()))
    socket:WebSocket
    connected_at:datetime = Field(default_factory=lambda:datetime.now(timezone.utc))
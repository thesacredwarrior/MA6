from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional


class Item(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int]
    item_name: str
    amount: int
    price: int
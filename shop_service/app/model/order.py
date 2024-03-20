from pydantic import BaseModel, ConfigDict
from typing import List

class OrderItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_name: str
    amount: int
    price: int

class Order(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    customer_name: str
    items: List[OrderItem]
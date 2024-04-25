from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str
    jobid: Optional[str]=''
    perpage: Optional[str] = 'no'
    meta: Optional[dict]={}
    output: Optional[str]='xlsx'
    filename: Optional[str] = ''

class ChatsUpdate(BaseModel):
    chats: str

class SetConfigRequest(BaseModel):
    yaml:str
class CustomerPurchase(BaseModel):
    customer_id: int = Field(..., description="The unique identifier of the customer")
    product_id: int = Field(..., description="The unique identifier of the financial product")
    purchase_date: Optional[datetime] = Field(..., description="The date when the purchase was made")

class ProductIds(BaseModel):
    category: int
    product_id:Optional[int]
    desc:Optional[str]

class OptionalRequest(BaseModel):
    jobid: Optional[str] = ''
from typing import Optional,List
from pydantic import BaseModel
from datetime import datetime


class UserAgent(BaseModel):
    id:Optional[int]
    number: str
    email: str
    password: str
    company_name: str
    owner_name: str
    r_package: int
    usage_token:str
    merchantUid: str
    apiUserId: str
    apiKey: str
    status:bool
    registred_date: datetime


class RequestPackage(BaseModel):
    id:Optional[int]
    name:str
    requests_count:int
    price_per_month:float



# PIPE 
class SellMeProducts(BaseModel):
    id:Optional[int]
    agent_number_or_email:str
    client_number:str
    p_price:float
    p_title:str
    p_info:str


class SendMeMessages(BaseModel):
    id:Optional[int]
    agent_number_or_email:str
    clients_number:List[str]
    message_desc:str


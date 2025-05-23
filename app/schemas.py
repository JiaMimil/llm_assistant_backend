from pydantic import BaseModel, EmailStr
from typing import List, Optional

# 用户相关模型
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    is_admin: bool = False 

class UserResponse(UserBase):
    id: int
    is_admin: bool 
    
    class Config:
        from_attributes = True

# Token相关模型
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# 聊天相关模型
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str
    status_code: int = 200
    message: str = "成功"

# 聊天历史相关模型
class ChatHistoryRequest(BaseModel):
    history: List[dict]

class ChatHistoryResponse(BaseModel):
    reply: str
    status_code: int = 200
    message: str = "成功"

# 摘要相关模型
class SummaryResponse(BaseModel):
    summary: str
    status_code: int = 200
    message: str = "成功"
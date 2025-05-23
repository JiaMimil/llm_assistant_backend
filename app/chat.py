from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import openai
import os
import httpx
from dotenv import load_dotenv

from app.schemas import ChatRequest, ChatResponse, ChatHistoryRequest, ChatHistoryResponse
from app.auth import get_current_user, get_db
from app.models import User

router = APIRouter()
load_dotenv()
# 使用正确的方式初始化OpenAI客户端
proxies = {
    "http://": "http://127.0.0.1:7897",
    "https://": "http://127.0.0.1:7897",
}
http_client = httpx.Client(proxies=proxies)
# 使用正确的方式初始化OpenAI客户端
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://free.v36.cm/v1/",
    http_client=http_client
)

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    body: ChatRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    单轮智能问答接口
    
    用户提交问题，系统调用大语言模型返回回答
    
    需要用户认证
    """
    print(f"用户 {current_user.username} 发送请求：", body)
    user_message = body.message
    
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "user", "content": user_message},
            ],
        )
        reply = completion.choices[0].message.content
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"调用AI服务失败: {str(e)}")

@router.post("/history", response_model=ChatHistoryResponse)
async def chat_with_history(
    body: ChatHistoryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    多轮对话接口
    
    用户提交对话历史，系统调用大语言模型继续对话
    
    需要用户认证
    """
    print(f"用户 {current_user.username} 发送历史对话请求：", body)
    history = body.history
    
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=history,
        )
        reply = completion.choices[0].message.content
        return ChatHistoryResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"调用AI服务失败: {str(e)}")

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import openai
import os
import httpx
from dotenv import load_dotenv

from app.schemas import SummaryResponse
from app.auth import get_current_user, get_db
from app.models import User

router = APIRouter()
load_dotenv()
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


@router.post("/", response_model=SummaryResponse)
async def summarize(
    file: UploadFile = File(...), 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    讲义自动摘要接口
    
    用户上传txt格式讲义文件，系统调用大模型生成5条要点摘要
    
    需要用户认证
    """
    # 检查文件类型
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="只支持txt格式文件")
    
    try:
        content = await file.read()
        text = content.decode("utf-8")
        prompt = f"请你将以下讲义内容提炼成五条要点：\n{text}\n"
        
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        summary = completion.choices[0].message.content
        return SummaryResponse(summary=summary)
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="文件编码错误，请确保是UTF-8编码的文本文件")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理摘要失败: {str(e)}")

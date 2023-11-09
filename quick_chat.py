from langchain.chat_models import ChatOpenAI
from langchain.schema.messages import HumanMessage, SystemMessage

import logging, os
from dotenv import load_dotenv

load_dotenv()

logging.getLogger().setLevel(logging.INFO)

# 设置网络代理
os.environ["http_proxy"] = "http://127.0.0.1:7890"
os.environ["https_proxy"] = "http://127.0.0.1:7890"

api_key = os.getenv("OPENAI_API_KEY")

chat = ChatOpenAI(model="gpt-4-vision-preview", max_tokens=256)

response = chat.invoke([
    HumanMessage(
            content=[
                {"type": "text", "text": "下面这张图片是什么内容?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://upload.wikimedia.org/wikipedia/zh/f/f8/Super_Mario_Bros_Wonder_Boxart.png",
                        "detail": "auto",
                    },
                },
            ]
        )
])

print(response)
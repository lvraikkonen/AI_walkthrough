from typing import List
from pydantic import BaseModel, Field, ConfigDict

from openai import AsyncOpenAI
from fastapi import FastAPI


class SearchQuery(BaseModel): 
    product_name: str
    query: str = Field(
        ...,
        description="""A descriptive query to search for the product, include 
        adjectives, and the product type. will be used to serve relevant 
        products to the user.""",
    )


class MultiSearchQueryResponse(BaseModel): 
    products: List[SearchQuery]

    model_config = ConfigDict(
      json_schema_extra={
            "examples": [
                {
                    "products": [
                        {
                            "product_name": "Nike Air Max",
                            "query": "black running shoes",
                        },
                        {
                            "product_name": "Apple iPhone 13",
                            "query": "smartphone with best camera",
                        },
                    ]
                }
            ]
        }
    )

from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=openai_api_key)

app = FastAPI(
    title="Ecommerce Vision API",
    description="""A FastAPI application to extract products 
        from images and describe them as an array of queries""",
    version="0.1.0",
)


class ImageRequest(BaseModel): 
    url: str
    temperature: float = 0.0
    max_tokens: int = 1800

    model_config = ConfigDict( 
      json_schema_extra={
            "examples": [
                {
                    "url": "https://mensfashionpostingcom.files.wordpress.com/2020/03/fbe79-img_5052.jpg?w=768",
                    "temperature": 0.0,
                    "max_tokens": 1800,
                }
            ]
        }
    )

@app.post("/api/extract_products", response_model=MultiSearchQueryResponse) 
async def extract_products(image_request: ImageRequest) -> MultiSearchQueryResponse: 
    completion = await client.chat.completions.create(
        model="gpt-4-vision-preview", 
        max_tokens=image_request.max_tokens,
        temperature=image_request.temperature,
        stop=["```"],
        messages=[
            {
                "role": "system",
                "content": f"""
                You are an expert system designed to extract products from images for 
                an ecommerce application. Please provide the product name and a 
                descriptive query to search for the product. Accurately identify every 
                product in an image and provide a descriptive query to search for the 
                product. You just return a correctly formatted JSON object with the 
                product name and query for each product in the image and follows the 
                schema below:

                JSON Schema:
                {MultiSearchQueryResponse.model_json_schema()}""", 
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """Extract the products from the image, 
                        and describe them in a query in JSON format""",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": image_request.url},
                    },
                ],
            },
            {
                "role": "assistant",
                "content": "```json", 
            },
        ],
    )
    return MultiSearchQueryResponse.model_validate_json(completion.choices[0].message.content)


if __name__=='__main__':
    import uvicorn
    # uvicorn app:app --reload
    uvicorn.run(app, port=8088)
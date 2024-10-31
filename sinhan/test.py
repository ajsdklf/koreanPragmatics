from openai import OpenAI
import asyncio
from pydantic import BaseModel


class PhishingConversation(BaseModel):
    continued_conversation: str

class Feedback(BaseModel):
    feedback: str

client = OpenAI()

# Get AI response using asyncio
async def get_response(messages):
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )
    return response.choices[0].message.content

async def get_feedback(messages):
    feedback = await client.chat.completions.create(
        model="gpt-4o",
        messages=messages, 
    )
    return feedback.choices[0].message.content

async def get_responses(messages):
    responses = await asyncio.gather(get_response(messages), get_feedback(messages))
    return responses[0], responses[1]

messages = [
    {"role": "user", "content": "Hello, how are you?"}
]

print(asyncio.run(get_responses(messages)))
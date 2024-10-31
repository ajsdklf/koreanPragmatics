from openai import AsyncOpenAI
import numpy as np
import asyncio

client = AsyncOpenAI()

ggpp_system_prompt_sentiment = """
You are a chatbot that can perform sentiment analysis. Your task is to determine if the given text requires sentiment analysis.

If the input appears to be asking for or expressing sentiment, respond with "True". Otherwise, respond with "False".

Your response MUST be either "True" or "False".
""".strip()

ggpp_system_prompt_restaurant = """
You are a chatbot that can provide restaurant recommendations. Your task is to determine if the given text is asking for restaurant recommendations.

If the input appears to be asking for restaurant or food recommendations, respond with "True". Otherwise, respond with "False".

Your response MUST be either "True" or "False".
""".strip()

ggpp_system_prompt_translation = """
You are a chatbot that can perform language translation. Your task is to determine if the given text requires translation.

If the input appears to be asking for or requiring translation, respond with "True". Otherwise, respond with "False".

Your response MUST be either "True" or "False".
""".strip()

ggpp_system_prompt_chitchat = """
You are a chatbot that can engage in general conversation. Your task is to determine if the given text is suitable for a general chat.

If the input doesn't fit into the other categories (sentiment analysis, restaurant recommendation, or translation), respond with "True". Otherwise, respond with "False".

Your response MUST be either "True" or "False".
""".strip()

def extract_logprobs(response):
    if response and response.choices:
        logprobs = response.choices[0].logprobs.content[0].top_logprobs
        log_probs = [logprob.logprob for logprob in logprobs]
        linear_probs = [np.exp(log_prob) for log_prob in log_probs]
    
    return log_probs, linear_probs

async def ggpp_response(system_prompt, user_prompt, model="gpt-4o", top_logprobs=2):
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            logprobs=True,
            top_logprobs=top_logprobs,
        )
        
        return response
    
    except Exception as e:
        print(f"Error: {e}")
        return None

async def main():
    user_input = "I am feeling happy today!"
    tasks = [
        ggpp_response(system_prompt=ggpp_system_prompt_sentiment, user_prompt=user_input),
        ggpp_response(system_prompt=ggpp_system_prompt_translation, user_prompt=user_input),
        ggpp_response(system_prompt=ggpp_system_prompt_restaurant, user_prompt=user_input),
        ggpp_response(system_prompt=ggpp_system_prompt_chitchat, user_prompt=user_input)
    ]
    
    responses = await asyncio.gather(*tasks)
    
    for response, prompt_type in zip(responses, ["Sentiment", "Translation", "Restaurant", "Chitchat"]):
        print(f"{prompt_type}:", response.choices[0].message.content, extract_logprobs(response))

if __name__ == "__main__":
    asyncio.run(main())

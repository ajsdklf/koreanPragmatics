from openai import OpenAI 
import json 

client = OpenAI()

FUNCTION_CALLER = """
As an input, you will be given a conversation between the user and the AI assistant. When given the enough information in the converstaion, you need to call a function named 'KOREAN_TEACHER' to generate a example sentence in Korean. Followings are the information you need to call function:

###
1. Context user wants to use to generate a example sentence in Korean.
2. Specific sentence in English that user wants to translate into Korean.
###

When given those infomrations, you need to call the function 'KOREAN_TEACHER' to generate a example sentence in Korean. 
"""

messages = [
  {'role': 'system', 'content': FUNCTION_CALLER},
  {'role': 'user', 'content': 'Hello'},
  {'role': 'assistant', 'content': 'Hello! How are you doing?'},
  {'role': 'user', 'content': 'I am doing great! I am excited to learn Korean!'},
  {'role': 'assistant', 'content': 'That is great to hear! I can help you with that. What do you want to learn in Korean?'},
  {'role': 'user', 'content': 'I want to learn how to say "I am going to the store" in Korean. I also want many example sentences that is used in making an order in restaurant.'}
]

tools = [
  {
    'type': 'function',
    'function': {
      'name': 'KOREAN_TEACHER',
      'description': 'Create exmaple sentences and explanation in Korean.',
      'parameters': {
        'type': 'object',
        'properties': {
          'context': {
            'type': 'string',
            'description': 'Context user wants to use to generate a example sentence in Korean.'
          },
          'sentence': {
            'type': 'string',
            'description': 'Specific sentence in English that user wants to translate into Korean.'
          },
        },
        'required': [
        'context',
        'sentence'
        ]
      }
    }
  }
]

response = client.chat.completions.create(
  model='gpt-4o',
  messages=messages,
  tools=tools,
  tool_choice='auto'
)

tool_calls = response.choices[0].message.tool_calls

# print(tool_calls)
print(tool_calls[0].function.name)
print(tool_calls[0].function.arguments)
args = tool_calls[0].function.arguments

dic = json.loads(args)
print(dic['context'])
print(dic['sentence'])
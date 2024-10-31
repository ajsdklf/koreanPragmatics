from openai import OpenAI
import requests
from datetime import datetime
import math
import json

client = OpenAI()

# Define the OpenAI function
tools = [
    {
        "type": "function",
        'strict': 'true',
        "function": {
            "name": "calculate_call_option_price",
            "description": "Calculate the price of a call option using the Black-Scholes formula",
            "parameters": {
                "type": "object",
                "properties": {
                    "S": {
                        "type": "number",
                        "description": "Current stock price"
                    },
                    "K": {
                        "type": "number",
                        "description": "Option strike price"
                    },
                    "T": {
                        "type": "number",
                        "description": "Time to expiration (in years)"
                    },
                    "r": {
                        "type": "number",
                        "description": "Risk-free interest rate"
                    },
                    "sigma": {
                        "type": "number",
                        "description": "Stock price volatility"
                    }
                },
                "required": ["S", "K", "T", "r", "sigma"]
            }
        }
    }
]

def calculate_call_option_price(S, K, T, r, sigma):
    # Black-Scholes formula for call option price
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    N_d1 = 0.5 * (1 + math.erf(d1 / math.sqrt(2)))
    N_d2 = 0.5 * (1 + math.erf(d2 / math.sqrt(2)))
    
    call_price = S * N_d1 - K * math.exp(-r * T) * N_d2
    return call_price

# Example usage of the OpenAI function
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Calculate the price of a call option with the following parameters: stock price $100, strike price $110, time to expiration 1 year, risk-free rate 5%, and volatility 20%."}
    ],
    tools=tools,
    tool_choice="auto"
)

print(response)

# Check if there are any tool calls in the response
if response.choices[0].message.tool_calls:
    tool_call = response.choices[0].message.tool_calls[0]
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    S = arguments.get("S")
    K = arguments.get("K")
    T = arguments.get("T")
    r = arguments.get("r")
    sigma = arguments.get("sigma")

    call_price = calculate_call_option_price(S, K, T, r, sigma)

    messages = [
        {"role": "user", "content": "Calculate the price of a call option with the following parameters: stock price $100, strike price $110, time to expiration 1 year, risk-free rate 5%, and volatility 20%."},
        response.choices[0].message,
        {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": str(call_price),
        }
    ]

    final_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    print(final_response.choices[0].message.content)
else:
    print("No tool calls were made in the initial response.")
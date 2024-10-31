import streamlit as st 
from openai import OpenAI 
from openai import AsyncOpenAI 
import asyncio 
from pydantic import BaseModel
from typing import List, Dict

client = OpenAI()
client_async = AsyncOpenAI()

st.header("Career Experience Helper")


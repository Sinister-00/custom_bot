import openai
from dotenv import load_dotenv, find_dotenv
import os
import logging
import time
from datetime import datetime
import streamlit as st


load_dotenv()

thread_id=os.getenv('THREAD_ID_OMNIBOT')
assist_id=os.getenv('ASSISTANT_ID_OMNIBOT')

client =openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))


# To be completed...
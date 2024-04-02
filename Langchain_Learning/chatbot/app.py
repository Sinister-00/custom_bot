from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
import streamlit as st
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

prompt=ChatPromptTemplate.from_messages(
    [
    ("system", "You are a helpful coding assistant. You are helping a user who is a competitive programmer. The user is trying to solve a problem on LeetCode. The user is stuck and asks for your help."),
    ("user", "Question:{Question}"),
])


# streamlit app
st.title("Langchain OpenAI Chat")
input_text = st.text_area("Ask your question here! 🤖")

llm= ChatOpenAI(
    model="gpt-3.5-turbo"
)


output_parser = StrOutputParser()

chain = prompt|llm|output_parser

if input_text:
    st.write(chain.invoke({"Question": input_text}))

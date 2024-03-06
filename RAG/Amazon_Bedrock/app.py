import json
import os 
import sys
import boto3


# Using AWS Titan model to generate embeddings


from langchain_community.embeddings import BedrockEmbeddings
from langchain.llms.bedrock import Bedrock


# imports for Data ingesion
import pypdf
import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader

# imports for Vector embedding and vector store

from langchain_community.vectorstores import FAISS
# from langchain.vectorstores import FAISS


from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA


# Creating Bedrock client 
bedrock = boto3.client(service_name='bedrock-runtime')
bedrock_embeddings = BedrockEmbeddings(model_id='amazon.titan-embed-text-v1',client=bedrock)


# Setting up data ingession
def data_ingesion():
    load=PyPDFDirectoryLoader("Data")
    documents=load.load()
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=10000,chuck_overlap=1000)
    docs=text_splitter.split_documents(documents)
    return docs

# vector embeddings and vector store
def get_vector_store(docs):
    vectorstore_faiss=FAISS.from_documents(
        docs,
        bedrock_embeddings
    )
    vectorstore_faiss.save_local("faiss_index")

# claude llm creation
    
def create_claude_llm():
    # create anthropic model
    llm=Bedrock(model_id="anthropic.claude-v2:1",client=bedrock,model_kwargs={"max_tokens": 512})
    return llm


         
def create_llama2_llm():
    # create anthropic model
    llm=Bedrock(model_id="meta.llama2-13b-chat-v1",client=bedrock,model_kwargs={"max_gen_len": 512})
    return llm

prompt_template="""
Human: You are a assistant chatbot for vinculum solutions and you are here to help me with my queries.
use the following peices of context to provide a consise answer to the question at the end but atleast summarize with 250 words.
along with the detailed explanations. if you dont't know the answer, just say "I can't answer that question try contacting this email id: swapnil@vinculumgroup.com", don't try to make up an answer.
<context>
{context}
</context>
Question: {question}

Asisstant:
"""

PROMPT=PromptTemplate(template=prompt_template,input_variables=["context","question"])

def get_response_llm(llm,vectorstore_faiss,query):
    qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore_faiss.as_retriever(
        search_type="similarity", search_kwargs={"k": 3}
    ),
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)
    answer=qa({"query":query})
    return answer['result']


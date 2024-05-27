from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
# from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from llama_index.core import SimpleDirectoryReader
from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from flask import Flask, request, jsonify


question = "how can i setup auto label printing"
embedding = OpenAIEmbeddings()
persist_directory = 'docs/chroma/'
vectordb = Chroma(
    persist_directory=persist_directory,
    embedding_function=embedding
)
# from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=vectordb.as_retriever()
)

result = qa_chain.invoke({"query": question})
print(result["result"])
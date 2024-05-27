from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from llama_index.core import SimpleDirectoryReader
from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
    
def create_chunks():
    text_splitter = CharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 200
    )
    dynamic_path = f'./data/'
    loader = DirectoryLoader(dynamic_path, glob="./*.txt", loader_cls=TextLoader)
    documents = loader.load()
    splits = text_splitter.split_documents(documents=documents)
    return splits


def create_embeddings():
    global persist_directory
    print(f"Persist directory: {persist_directory}")
    embedding = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(
        documents=create_chunks(),
        embedding=embedding,
        persist_directory=persist_directory
    ) 
    vectordb.persist()
    print(f"Number of documents: {vectordb._collection.count()}")
    return vectordb

def similarity_search_with_score(question, vectordb, k=3):
    docs = vectordb.similarity_search_with_score(question, k=k)
    print("Similarity search results:")
    for doc, score in docs:
        print(f"Score: {score}")
        print(doc.page_content)
        print("\n")
    return docs

def load_embeddings_from_local():
    global persist_directory
    
    embedding=OpenAIEmbeddings(
        persist_directory=persist_directory,
        model_name="gpt-3.5-turbo"
    )
    vectordb = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding
    )
    return vectordb


def ask_query(vectordb,question):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=vectordb.as_retriever()
    )
    result = qa_chain.invoke({"query": question})
    print(result["result"])
    return result["result"]

def qa_chain_with_template(vectordb,question):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    template = """Address the user as vinner and Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. 
    {context}
    Question: {question}
    Helpful Answer:"""
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=vectordb.as_retriever(),
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    )
    result = qa_chain.invoke({"query": question})
    print(f"Question: {question} \n Answer: {result['result']} \n")
    return result["result"]



def create_chat_memory(vectordb):
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    qa = ConversationalRetrievalChain.from_llm(
        llm,
        retriever=vectordb.as_retriever(),
        memory=memory
    )
    return qa

def ask_query_with_chat_memory(qa, question):
    result = qa.invoke({"question": question})
    print(f"Question: {question} \n Answer: {result['answer']} \n")
    return result['answer']

# Function to create or load embeddings
def get_or_create_embeddings():
    global persist_directory
    try:
        vectordb = load_embeddings_from_local()
        print("Embeddings loaded from local.")
    except FileNotFoundError:
        print("Embeddings not found, creating new...")
        embedding = OpenAIEmbeddings()
        vectordb = Chroma.from_documents(
            documents=create_chunks(),
            embedding=embedding,
            persist_directory=persist_directory
        )
        vectordb.persist()
    return vectordb
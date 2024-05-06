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


# ::TODO::
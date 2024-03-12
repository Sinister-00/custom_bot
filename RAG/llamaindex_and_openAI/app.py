import openai 
import os
import time
import streamlit as st
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.response.pprint_utils import pprint_response
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage
)

load_dotenv()
st.set_page_config(
    page_title="VinAi Chatbot",
    page_icon="🤖",
)
if "thread_id" not in st.session_state:
    st.session_state.thread_id=None

assist_id=os.getenv('ASSISTANT_ID_OMNIBOT')

def loadData(d):
    documents=SimpleDirectoryReader(d).load_data()
    return documents

def createIndex(documents):
    index=VectorStoreIndex(documents, show_progress=True)
    return index

def createQueryEngine(index):
    query_engine=index.as_query_engine() 
    return query_engine

def createQueryEngineWithCutOff(index,cutoff=0.92,):
    retriever=VectorIndexRetriever(index=index)
    postProcessor=SimilarityPostprocessor(similarity_cutoff=cutoff)
    query_engine=RetrieverQueryEngine(retriever=retriever,node_postprocessors=[postProcessor])
    return query_engine

def execute_query(q, query_engine):
    q = str(q)
    response = query_engine.query(q)
    return response

PERSIST_DIR = "./storage"

def createRAGIndex(dataDir):
    documents=loadData(dataDir)
    index=createIndex(documents)
    query_engine=createQueryEngine(index)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
    print("Done creating the RAG index")
    return query_engine

def createRAGIndexWithCutOff(dataDir,cutoff):
    documents=loadData(dataDir)
    index=createIndex(documents)
    query_engine=createQueryEngineWithCutOff(index,cutoff)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
    return query_engine

def loadRAGIndex():
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)
    query_engine = createQueryEngine(index)  
    print("Successfully loaded the RAG index")
    return query_engine

users = {
    "swapnil@vinculumgroup.com": {"password": "user1password"},
    "demo": {"password": "admindemo"},
    "user3@example.com": {"password": "user3password"}
}
placeholder = st.empty()


if "messages" not in st.session_state:
    st.session_state.messages = {"RAG": [], "OpenAI": []}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    with placeholder.form("login"):
        st.markdown("#### Enter your credentials")
        email = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            with st.spinner("Wait for it..."):
                time.sleep(3)

    if submit and email in users and password == users[email]["password"]:
        with st.spinner("Login Success..."):
            time.sleep(2)
            st.session_state.logged_in = True
        placeholder.empty()

    elif submit and (email not in users or password != users[email]["password"]):
        st.error("Login failed")

if st.session_state.logged_in:

    if 'query_engine' not in st.session_state:
        st.session_state.query_engine = "Not yet loaded"

    st.header("Chat with VinAi using RAG & Open AI Assistant 💁")


    with st.sidebar:
        st.title("Update Or Create Vector Store:")
        update_vector_store = st.radio("Update Vector Store", ("Yes", "No"),)
        if update_vector_store == "Yes":
            st.write("You chose to update the vector store")
            directory=st.text_input("Enter the directory path") 
            if directory and os.path.exists(directory):
                st.success("Directory exists")
                if st.button("Update Vector Store"):
                    with st.spinner("Processing..."):
                        st.session_state.query_engine = createRAGIndex(directory)
                        st.success("Done updating the vector store")
            elif directory and not os.path.exists(directory):
                st.error("Please enter the directory path")
            

        else:
            if st.button("Load Vector Store"):
                with st.spinner("Processing..."):
                    st.session_state.query_engine = loadRAGIndex()
                    st.success("Done loading the vector store")


    st.sidebar.title("Choose the Assistant:")
    st.session_state.assistant = st.sidebar.radio("Choose the Assistant", ("RAG", "OpenAI Assistant"),)


    if st.session_state.query_engine == "Not yet loaded":
        st.error("Please load or update the vector store first.")
    elif st.session_state.assistant == "RAG" and st.session_state.query_engine != "Not yet loaded":
        
        messages = st.session_state.messages["RAG"]

        if "RAG" not in st.session_state.messages:
            st.session_state.messages["RAG"] = []

        for message in st.session_state.messages["RAG"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt:=st.chat_input("Ask you query here"):
            st.session_state.messages["RAG"].append({"role":"user","content":prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.spinner("Wait... Generating response..."):
                response = execute_query(prompt, st.session_state.query_engine)
            st.session_state.messages["RAG"].append({"role":"assistant","content":response.response})
            with st.chat_message("assistant"):
                st.markdown(response.response, unsafe_allow_html=True)

    elif st.session_state.assistant == "OpenAI Assistant" and st.session_state.query_engine != "Not yet loaded":

        messages = st.session_state.messages["OpenAI"]

        if "OpenAI" not in st.session_state.messages:
            st.session_state.messages["OpenAI"] = []

        for message in st.session_state.messages["OpenAI"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        client =openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        chat_thread=client.beta.threads.create()
        st.session_state.thread_id=chat_thread.id
        st.sidebar.write("Chat thread id:",chat_thread.id)
        if "opneai_model"  not in st.session_state:
            st.session_state.openai_model="gpt-3.5-turbo-1106"


        if prompt:=st.chat_input("Ask you query here"):
            st.session_state.messages["OpenAI"].append({"role":"user","content":prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            client.beta.threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=prompt
            )
            run=client.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=assist_id,
                instructions="""
                Please address the user as "Vinner" and ask the user if he/she has any queries related to vinculum solutions. only respond if you know the context do not try to generate on your own.
                """
            )
            with st.spinner("Wait... Generating response..."):
                while run.status != "completed":
                    time.sleep(1)
                    run=client.beta.threads.runs.retrieve(thread_id=st.session_state.thread_id,run_id=run.id)
                    messages=client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
                    assistant_message_for_run=[
                        message for message in messages if message.run_id==run.id and message.role == "assistant"
                    ]

                for message in assistant_message_for_run:
                    full_response=message.content[0].text.value
                    st.session_state.messages["OpenAI"].append(
                        {"role": "assistant", "content": full_response}
                    )
                    with st.chat_message("assistant"):
                        st.markdown(full_response, unsafe_allow_html=True)


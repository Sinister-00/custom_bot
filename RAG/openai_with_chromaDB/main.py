from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_chroma import Chroma
# from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from llama_index.core import SimpleDirectoryReader
from langchain_community.document_loaders import DirectoryLoader
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
import streamlit as st
import openai
from pymongo import MongoClient
import base64
import json
from streamlit_oauth import OAuth2Component
import os
import pytz
import time
import streamlit as st
from datetime import datetime
import bcrypt
from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"]=os.getenv("OPENAI_API_KEY")
assist_id=os.getenv('ASSISTANT_ID_OMNIBOT')
CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI")
AUTHORIZE_ENDPOINT = "https://accounts.google.com/o/oauth2/auth"
TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
REVOKE_ENDPOINT = "https://oauth2.googleapis.com/revoke"
ist = pytz.timezone('Asia/Kolkata')
uri = os.getenv('MONGO_URI')
client = MongoClient(uri)
db = client["VinAi"]

rag_messages_collection = db["rag_messages"]
assistant_messages_collection = db["assistantAPI_messages"]

users_collection = db["users"]


def check_credentials(email, password):
    user = users_collection.find_one({"email": email})
    if user:
        hashed_password = user["password"]
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return True
    return False

def retrieve_messages(user_email):
    rag_messages = rag_messages_collection.find({"user_email": user_email})
    assistant_messages = assistant_messages_collection.find({"user_email": user_email})
    return rag_messages, assistant_messages

def format_timestamp(timestamp):
    dt_object = datetime.fromtimestamp(timestamp)
    ist = pytz.timezone('Asia/Kolkata')
    dt_ist = dt_object.astimezone(ist)
    formatted_timestamp = dt_ist.strftime('%d-%b-%Y %H-%M-%S') 
    return formatted_timestamp


st.set_page_config(
    page_title="VinAi Chatbot",
    page_icon="🤖",  
)
if "thread_id" not in st.session_state:
    st.session_state.thread_id=None

placeholder = st.empty()


if "messages" not in st.session_state:
    st.session_state.messages = {"RAG": [], "OpenAI": []}
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "memory_chain" not in st.session_state:
    st.session_state.memory_chain = None


DATA_DIR = "./data/"
PERSIST_DIR = "./docs/chroma/"

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
    create_chunks()
    embedding = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(
        documents=create_chunks(),
        embedding=embedding,
        persist_directory=PERSIST_DIR
    )
    # vectordb.persist() # new version of chroma does not need to persist
    print(f"Number of documents: {vectordb._collection.count()}")
    return vectordb

def similarity_search_with_score(question, vectordb, k=3):
    docs = vectordb.similarity_search_with_score(question, k=k)
    print("Similarity search results:")
    for result in docs:
        print("\n")
        print(f"Score: {result[1]}")
        print(f"Content: {result[0].page_content}")
    return docs

def load_embeddings_from_local():
    embedding=OpenAIEmbeddings()
    vectordb = Chroma(
        persist_directory=PERSIST_DIR,
        embedding_function=embedding
    )
    return vectordb


def create_chain_with_template():
    template = """Address the user as vinner and Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer. 
    {context}
    Question: {question}
    Helpful Answer:"""
    
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)
    
    vectordb = load_embeddings_from_local()
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=vectordb.as_retriever(),
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    )
    return qa_chain

def run_chain_with_template(question):
    qa_chain = create_chain_with_template()
    result = qa_chain.invoke({"query": question})
    print(result["result"])
    return result["result"]


def create_memory_chain():
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    vectordb = load_embeddings_from_local()
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    qa = ConversationalRetrievalChain.from_llm(
        llm,
        retriever=vectordb.as_retriever(),
        memory=memory
    )
    return qa

def run_memory_chain(question, qa):
    result = qa.invoke({"question": question})
    print(result)
    print("-------------------")
    return result['answer']



if not st.session_state.logged_in:
    with placeholder.form("login"):
        st.markdown("#### Enter your credentials")
        email = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")


        if submit:
            with st.spinner("Authenticating..."): 
                time.sleep(2)

            if  check_credentials(email, password):
                with st.spinner("Login Success..."):
                    time.sleep(2)
                    st.session_state.logged_in = True
                    st.session_state.user_mail = email
                placeholder.empty()

            elif not check_credentials(email, password):
                st.error("Login failed")
    
    
    
    if "auth" not in st.session_state and not st.session_state.logged_in:
        oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET,
                              AUTHORIZE_ENDPOINT,
                                TOKEN_ENDPOINT,
                                  TOKEN_ENDPOINT,
                                    REVOKE_ENDPOINT)
        result = oauth2.authorize_button(
            name="Continue with Google",
            icon="https://www.google.com.tw/favicon.ico",
            redirect_uri=REDIRECT_URI,
            scope="openid email profile",
            key="google",
            extras_params={"prompt": "consent", "access_type": "offline"},
            use_container_width=True,
            pkce='S256',
            )
        # print(result)
        if result:
            st.empty()

            id_token = result["token"]["id_token"]
            payload = id_token.split(".")[1]
            payload += "=" * (-len(payload) % 4)
            payload = json.loads(base64.b64decode(payload))
            # print("Payload: ", payload)
            name= payload["name"]
            isVerified = payload["email_verified"]
            pfp = payload["picture"]
            email = payload["email"]
            st.session_state["auth"] = email

            st.session_state["token"] = result["token"]
            if email.split("@")[1] == "vinculumgroup.com": 
                google_oauth_login_collection = db["google-oauth-login"]
                google_oauth_login_collection.insert_one({
                    "name": name,
                    "email": email,
                    "isVerified": isVerified,
                    "pfp": pfp,
                    "timestamp": format_timestamp(time.time())
                })  
                st.session_state.user_mail = email
                st.session_state.logged_in = True
                st.rerun()
            else:
                with st.spinner("Access Denied - Unauthorized Domain"):
                    # print(st.session_state["auth"])
                    del st.session_state["auth"]
                    time.sleep(2)
                    


    else:
        st.empty()
            


if st.session_state.logged_in:
    
    # if 'memory_chain' not in st.session_state:
    if st.session_state.logged_in and st.session_state.memory_chain is None:
        st.session_state.vectorDB = Chroma(
            persist_directory=PERSIST_DIR,
            embedding_function=OpenAIEmbeddings()
        )
        st.session_state.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        st.session_state.memory_chain = ConversationalRetrievalChain.from_llm(
            st.session_state.llm,
            retriever=st.session_state.vectorDB.as_retriever(),
            memory=ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
        )

    st.header("Chat with VinAi using RAG & Open AI Assistant 💁")


    # with st.sidebar:
        # st.title("Update Or Create Vector Store:")
        # update_vector_store = st.radio("Update Vector Store", ("Yes", "No"),)
        # if update_vector_store == "Yes":
        #     st.write("You chose to update the vector store")
        #     directory=st.text_input("Enter the directory path") 
        #     if directory and os.path.exists(directory):
        #         st.success("Directory exists")
        #         if st.button("Update Vector Store"):
        #             with st.spinner("Processing..."):
        #                 st.session_state.query_engine = createRAGIndex(directory)
        #                 st.success("Done updating the vector store")
        #     elif directory and not os.path.exists(directory):
        #         st.error("Please enter the directory path")
            

        # else:
        #     if st.button("Load Vector Store"):
        #         with st.spinner("Processing..."):
        #             st.session_state.query_engine = loadRAGIndex()
        #             st.success("Done loading the vector store")

    


    st.sidebar.title("Choose the Assistant:")
    st.session_state.assistant = st.sidebar.radio("Choose the Assistant", ("RAG", "OpenAI Assistant"),)


    if st.session_state.memory_chain == "Not yet loaded":
        st.error("Please load or update the vector store first.")
    elif st.session_state.assistant == "RAG" and st.session_state.memory_chain != "Not yet loaded":
        rag_messages, assistant_messages = retrieve_messages(st.session_state.user_mail)
        

        # messages = st.session_state.messages["RAG"]
        for message in rag_messages:
            st.session_state.messages["RAG"].append({"role": "user", "content": message["message_content"]})
            st.session_state.messages["RAG"].append({"role": "assistant", "content": message["response_content"]})
        
        
        messages = st.session_state.messages["RAG"]

        messages = st.session_state.messages["RAG"]

        if "RAG" not in st.session_state.messages:
            st.session_state.messages["RAG"] = []

        for message in st.session_state.messages["RAG"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt:=st.chat_input("Ask you query here"):
            # st.session_state.messages["RAG"].append({"role":"user","content":prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.spinner("Wait... Generating response..."):
                # response = execute_query(prompt, st.session_state.query_engine)
                # response=run_memory_chain(prompt,st.session_state.memory_chain)
                chain=st.session_state.memory_chain.invoke({"question": prompt})
                print(chain)
                response=chain["answer"]
                
            st.session_state.messages["RAG"].append({"role":"assistant","content":response})
            with st.chat_message("assistant"):
                st.markdown(response, unsafe_allow_html=True)
                
            rag_messages_collection.insert_one({

                "user_email": st.session_state.user_mail,
                "message_content": prompt,
                "response_content": response,
                "timestamp": format_timestamp(time.time())  # Add a timestamp if needed
            })

    elif st.session_state.assistant == "OpenAI Assistant" and st.session_state.query_engine != "Not yet loaded":

        rag_messages, assistant_messages = retrieve_messages(st.session_state.user_mail)

        for message in assistant_messages:
            st.session_state.messages["OpenAI"].append({"role": "user", "content": message["message_content"]})
            st.session_state.messages["OpenAI"].append({"role": "assistant", "content": message["response_content"]})


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
            # st.session_state.messages["OpenAI"].append({"role":"user","content":prompt})
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

            assistant_messages_collection.insert_one({
                "user_email": st.session_state.user_mail,
                "message_content": prompt,
                "response_content": full_response,
                "timestamp": format_timestamp(time.time())  # Add a timestamp if needed
            })

    
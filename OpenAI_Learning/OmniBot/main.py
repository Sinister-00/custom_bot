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


# initialize all the sessions

# file_id_list=[]
if "file_id_list" not in st.session_state:
    st.session_state.file_id_list=[]

if "start_chat" not in st.session_state:
    st.session_state.start_chat=False

if "thread_id" not in st.session_state:
    st.session_state.thread_id=None

#  Setup the fornt end page
    
st.set_page_config(
    page_title="OmniBot",
    page_icon="🤖",
)

# function definations
def upload_file_to_openai(filepath):
    """
    This function uploads the file to openai and returns the file id
    param1: filepath-> path of the file to be uploaded
    """
    with open(filepath, "rb") as file:
        response = client.files.create(file=file,purpose="assistants")
        file_id = response.id
    return file_id 

# side bar to upload the file
file_uploaded=st.sidebar.file_uploader("Upload the file",type=["txt","pdf","docx"],key="file_upload")

# upload file button and file id

if st.sidebar.button("Upload file"):
    if file_uploaded:
        with open(f"{file_uploaded.name}","wb") as f:
            f.write(file_uploaded.getbuffer())
        another_file_id=upload_file_to_openai(f"{file_uploaded.name}")
        st.session_state.file_id_list.append(another_file_id) 
        st.session_state.uploaded_file_name = file_uploaded.name
        st.sidebar.write(f"file id:: {another_file_id}")


# display file ids
if st.session_state.file_id_list:
    st.sidebar.write("Uploaded file ids")
    for file_id in st.session_state.file_id_list:
        st.sidebar.write(file_id) 
        # associate each file id with the current assistant
        assistant_file=client.beta.assistants.files.create(
            assistant_id=assist_id,
            file_id=file_id
        )


# button to initiate the chat
if st.sidebar.button("Start Chat"):
    if st.session_state.file_id_list:
        st.session_state.start_chat=True
        # create a new thread every time the chat is initiated
        chat_thread=client.beta.threads.create()
        st.session_state.thread_id=chat_thread.id
        st.sidebar.write(f"Thread id: {chat_thread.id}")
    else:
        st.sidebar.warning("No file found: Please upload the file first")


# the main interface
st.title("OmniBot")
st.write("This is a chatbot to assist you with the queries related to vinculum solutions")

# check sessions
if st.session_state.start_chat:
    if "opneai_model"  not in st.session_state:
        st.session_state.openai_model="gpt-3.5-turbo-0125"
    if "messages" not in st.session_state:
        st.session_state.messages=[]

    # get the message from the user exisiting in the session state
    for messages in st.session_state.messages:
        with st.chat_message(messages["role"]):
            st.markdown(messages["content"])
    
    # chat input for the user
    if prompt:=st.chat_input("Ask you query here"):
        # add user message in the state and display it
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

         # add the users message to the existing thread
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )
        #  create a run with additional instructions
        run=client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assist_id,
            instructions="""
            Please address the user as "Demo user " and ask the user if he/she has any queries related to vinculum solutions.
            """
        )
        # spinner to wait for the assistant to complete the run
        with st.spinner("Wait... Generating response..."):
            while run.status != "completed":
                time.sleep(1)
                run=client.beta.threads.runs.retrieve(thread_id=st.session_state.thread_id,run_id=run.id)
                # get the response from the assistant added
                messages=client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
                # process and display the assistant messages
                assistant_message_for_run=[
                    message for message in messages if message.run_id==run.id and message.role == "assistant"
                ]

            for message in assistant_message_for_run:
                # full_response = process_message_with_citations(message=message)
                # full_response=message.content
                full_response=message.content[0].text.value
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )
                with st.chat_message("assistant"):
                    st.markdown(full_response, unsafe_allow_html=True)


else:   
    st.write("Please upload the file and start the chat")
    st.stop()
     
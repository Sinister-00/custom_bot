import openai
from dotenv import load_dotenv, find_dotenv
import os
import logging
import time
from datetime import datetime


load_dotenv()


client= openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
model="gpt-3.5-turbo-0125"

# Step:1-> get the thread id and assistant id from the environment variable

thread_id=os.getenv('THREAD_ID_OMNIBOT')
assist_id=os.getenv('ASSISTANT_ID_OMNIBOT')

# Step:2-> create a message and add it to the thread

message="what are Advantages Of Omni Integration?"

message=client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=message,
)

# Step:3-> create a run with the assistant_id and thread_id

run=client.beta.threads.runs.create(
    assistant_id=assist_id,
    thread_id=thread_id,
    instructions="""
Please address the user as "Demo user " and ask the user if he/she has any queries related to vinculum solutions.
"""
)
def wait_for_run_to_complete(client,thread_id,run_id,sleeptime=5):
    """
    This function waits for the assistant to complete the run and print elapsed time
    param1: client-> openai client
    param2: assistant_id-> assistant id
    param3: thread_id-> thread id
    param4: sleeptime-> time to sleep before checking the status again
    """

    while True:
        try:
            run=client.beta.threads.runs.retrieve(thread_id=thread_id,run_id=run_id)
            if run.completed_at:
                elapsed_time=run.completed_at-run.created_at
                formatted_elapse_time=time.strftime("%H:%M:%S",time.gmtime(elapsed_time))
                print(f'run completed in {formatted_elapse_time}')
                logging.info(f'run completed in {formatted_elapse_time} ')
                message=client.beta.threads.messages.list(thread_id=thread_id)
                last_message=message.data[0]
                response=last_message.content[0].text.value
                print(f'Assistant: {response}')
                break
        except Exception as err:
            print('an error occured while retriving the run: ',err)
            logging.error(f'an error occured while retriving the run: {err}')
            break
        logging.info(f'waiting for the run to complete...')
        time.sleep(sleeptime)


# running the assistant
wait_for_run_to_complete(client=client,thread_id=thread_id,run_id=run.id)


# Step:4-> logging the steps
run_steps=client.beta.threads.runs.steps.list(
    run_id=run.id,
    thread_id=thread_id
)

# print(f'Steps------> {run_steps.data[0]}')
print(f'Steps------> {run_steps.data}')
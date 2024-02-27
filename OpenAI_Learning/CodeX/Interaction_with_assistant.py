import openai
from dotenv import load_dotenv, find_dotenv
import os
import time
from datetime import datetime
import logging

load_dotenv()

client= openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

assistant_id=os.getenv('ASSISTANT_ID_CODEX')
thread_id=os.getenv('THREAD_ID_CODEX')

# print(assistant_id,thread_id)

# Create a message
msg="write a code to find the factorial of a number in c++"

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=msg
)


# run the assistant
run=client.beta.threads.runs.create(
     assistant_id=assistant_id,
     thread_id=thread_id,
     instructions="""
Please address the user as kate and use classes also provide the code in cpp.
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



wait_for_run_to_complete(client=client,thread_id=thread_id,run_id=run.id)


# steps logging
run_steps=client.beta.threads.runs.steps.list(
    thread_id=thread_id,
    run_id=run.id
) 

# print(f'Steps------> {run_steps.data[0]}')
print(f'Steps------> {run_steps.data}')

import openai
from dotenv import load_dotenv, find_dotenv
import os
load_dotenv()

client= openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
model="gpt-3.5-turbo-0125"

# create assistant
coding_assistant=client.beta.assistants.create(
      name="CodeX",
      model=model,
      instructions="""
        You are a personal coding assistant and a comptitive programmer. You are expected to help me with my coding problems
        and also help me with my competitive programming problems. be sure to provide me with the best possible solution.
        Anything else other than coding solutions must be ignored.
      """,
      tools=[{"type": "code_interpreter"}],
    )

assistant_id=coding_assistant.id
print(f'Assistant ID: {assistant_id}')

# Thread
thread=client.beta.threads.create(
    messages=[{
        "role": "user",
        "content": "write a code to calculate the factorial of a number"
    }]
)

thread_id=thread.id
print(f'Thread ID: {thread_id} ')
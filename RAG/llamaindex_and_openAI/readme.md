Certainly! Here's the revised README with the steps adjusted to clone the repository first and then run all necessary commands using the Makefile:

# OmniBot  

## Project Overview
OmniBot is a chatbot developed using the RAG and Assistant API from OpenAI. It is trained on custom data to provide intelligent and context-aware responses to user queries.

## Deploying on AWS EC2 Instance
To deploy the app on an AWS EC2 instance, follow these steps:


1. Install Make if not already installed:
    ```bash
    sudo apt update
    sudo apt install make
    ```

2. Clone the project repository:
    ```bash
    git clone https://github.com/Sinister-00/custom_bot.git
    ```

3. Navigate to the working directory:
    ```bash
    cd custom_bot
    cd RAG
    cd llamaindex_and_openAI
    ```

4. Install dependencies and build the project using the Makefile:
    ```bash
    make build
    ```
    > **Info**  
    > If you encounter any error while running the make commands. Repeat the step-1 again.

5. Run all setup commands and setup `.env` using the Makefile:
    ```bash
    make config
    ```

6. Configure Nginx: Follow the instructions in the [Nginx README](./nginx/readme.md) to set up Nginx as
    a reverse proxy for your Streamlit application.

7. Run the Streamlit app:
    ```bash
    make run
    ```

8. *Optionally*, run the Streamlit app in the background using `nohup`:
    ```bash
    nohup python3 -m streamlit run app.py --server.port 8501 
    ```

This sequence of steps will clone the repository, navigate to the appropriate directory, run all necessary setup commands using the Makefile, configure Nginx, and finally run the Streamlit app. Adjustments can be made as needed for your specific setup.
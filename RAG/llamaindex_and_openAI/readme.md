# OmniBot  

## Project Overview
OmniBot is a chatbot developed using the RAG and Assistant API from OpenAI. It is trained on custom data to provide intelligent and context-aware responses to user queries.

## Deploying on AWS EC2 Instance
To deploy the app on an AWS EC2 instance, follow these steps:

1. Update package repositories:
    ```bash
    sudo apt update
    sudo apt-get update
    ```

2. Upgrade installed packages:
    ```bash
    sudo apt upgrade -y
    ```

3. Install necessary tools:
    ```bash
    sudo apt install git curl unzip tar make sudo vim wget -y
    sudo apt install python3-pip
    ```

4. Clone the project repository:
    ```bash
    git clone https://github.com/Sinister-00/custom_bot.git
    ```

5. Navigate to the working directory:
    ```bash
    cd custom_bot
    cd RAG
    cd llamaindex_and_openAI
    ```

6. Install Python dependencies:
    ```bash
    pip3 install -r requirements.txt
    ```

7. Create `.env` file for loading environment variables:

    ```
    touch .env
    ```

8. Using nano enter the environment variables into `.env`:
    ```
    nano .env
    ```
    > **Note**  
    > Refer `.example.env` for environment variables.

9. Run the Streamlit app:

    ```bash
    python3 -m streamlit run app.py --server.port 6969
    ```
    > **Info**  
    > Edit inbound rules and allow custom TCP port `6969` to everyone. 


10. Optionally, run the Streamlit app in the background using `nohup`:
    ```bash
    nohup python3 -m streamlit run app.py --server.port 6969 
    ```

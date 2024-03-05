# OmniBot  

## Project Overview
OmniBot is a chatbot developed using the Assistant API from OpenAI. It is trained on custom data to provide intelligent and context-aware responses to user queries.

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
    ```

4. Clone the project repository:
    ```bash
    git clone https://github.com/Sinister-00/custom_bot.git
    ```

5. Navigate to the OmniBot directory:
    ```bash
    cd custom_bot
    ```

6. Install Python dependencies:
    ```bash
    sudo apt install python3-pip
    pip3 install -r requirements.txt
    ```

7. Run the Streamlit app:
    ```bash
    python3 -m streamlit run main.py --server.port 6969
    ```

8. Optionally, run the Streamlit app in the background using `nohup`:
    ```bash
    nohup python3 -m streamlit run main.py --server.port 6969 &
    ```

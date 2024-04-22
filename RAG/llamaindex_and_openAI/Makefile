UPDATE_CMD=sudo apt update && sudo apt-get update && sudo apt upgrade -y && sudo apt install git curl unzip tar make sudo vim wget python3-pip -y
PIP_INSTALL_CMD=pip3 install -r requirements.txt
PYTHON_CMD=python3
STREAMLIT_CMD=python3 -m streamlit

PROJECT_DIR=$(shell pwd)

ENV_FILE=.env

ENV_VARIABLES=\
	OPENAI_API_KEY \
	MONGO_URI \
	ASSISTANT_ID_OMNIBOT \
	THREAD_ID_OMNIBOT \
	GOOGLE_CLIENT_ID \
	GOOGLE_CLIENT_SECRET \
	REDIRECT_URI \
	AUTHORIZE_ENDPOINT \
	TOKEN_ENDPOINT \
	REVOKE_ENDPOINT

config:
	@rm -f $(ENV_FILE)
	@touch $(ENV_FILE)
	@chmod 600 $(ENV_FILE)
	@for var in $(ENV_VARIABLES); do \
		read -p "Enter value for $$var: " value; \
		echo "$$var=\"$$value\"" >> $(ENV_FILE); \
	done
	@echo "Environment variables have been configured and saved in $(ENV_FILE)"

build:
	$(UPDATE_CMD)
	$(PIP_INSTALL_CMD)

run:
	$(PYTHON_CMD) create_storage.py
	$(STREAMLIT_CMD) run app.py

clean:
	rm -rf storage

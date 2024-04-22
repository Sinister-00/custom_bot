
FROM python:3.12.0

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y \
    git \
    curl \
    unzip \
    tar \
    vim \
    wget

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["python3","-m","streamlit", "run", "app.py"]

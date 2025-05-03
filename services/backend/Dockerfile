FROM python:3.11-buster

# Установка зависимостей для Docker
RUN apt-get update && \
    apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg2 \
    software-properties-common && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - && \
    echo "deb [arch=amd64] https://download.docker.com/linux/debian buster stable" > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-get install -y docker-ce-cli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Создание директории приложения
RUN mkdir app
WORKDIR /app

# Установка переменных окружения
ENV PATH="${PATH}:/root/.local/bin"
ENV PYTHONPATH=/app/src

# Копирование файла зависимостей и установка Python-зависимостей
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копирование исходного кода
COPY src/ .

# Установка точки входа (если необходимо)
# CMD ["python", "your_script.py"]
FROM python:3.10-slim
WORKDIR /app
RUN groupadd -r web && useradd -d /code -r -g web web \
    && chown web:web -R /code \
USER web
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
COPY --chown web:web ../requirements.txt ./app/
RUN pip3 install -U pip
RUN pip3 install -r /app/requirements.txt --no-cache-dir
COPY --chown web:web ../src ./app/

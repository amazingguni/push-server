FROM python:3.10

ENV PYTHONUNBUFFERED 1

RUN pip install poetry
RUN ln -fs /usr/share/zoneinfo/Asia/Seoul /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

RUN mkdir -p /app    
COPY poetry.lock pyproject.toml /app/
RUN poetry config virtualenvs.create false
RUN cd /app/ && poetry install -v --no-interaction --no-ansi

COPY . /app
WORKDIR /app
# Reinstall to install src directory
RUN poetry install -v --no-interaction --no-ansi
ENTRYPOINT ["bash", "/app/docker/docker-entrypoint.sh"]

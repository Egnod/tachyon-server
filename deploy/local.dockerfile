FROM python:3.9.6-slim-buster

RUN mkdir /app/
COPY ./ /app/

RUN pip install poetry==1.1.11

# Configuring poetry
RUN poetry config virtualenvs.create false

# Copying requirements of a project
WORKDIR /app/
COPY ./pyproject.toml ./poetry.lock /app/

RUN poetry install

CMD ["/usr/local/bin/monkeytype", "run", "-m", "tachyon"]

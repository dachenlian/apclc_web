FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
ADD . /code/
RUN pip install pipenv
WORKDIR /code/
RUN pipenv install --system

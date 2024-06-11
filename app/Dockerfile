# pull official base image
FROM python:3.8.3-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev jpeg-dev zlib-dev libffi-dev

# install dependencies
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
# RUN python -m pip install pip==19.3.1
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .

# copy project
COPY . .

EXPOSE 8000
EXPOSE 8001

# run entrypoint.sh
ENTRYPOINT [ "/usr/src/app/entrypoint.sh" ]
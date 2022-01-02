# the image on the basis of which we create a container
FROM python:3.8.10-alpine3.14

# working directory inside the project
WORKDIR /usr/src/app

# environment variables for python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Installing dependencies for Postgre
# we need some packages only for installation,
# and then we can take them down**
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \ 
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

# installing dependencies before calling COPY command
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN PYTHONPATH=/usr/bin/python pip install -r requirements.txt

# **we clean up unnecessary, minimizing the weight of dockers
RUN apk del .tmp-build-deps

# copy the contents of the current folder to the container
COPY . .

# add script launch entrypoint.sh when starting the container:
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

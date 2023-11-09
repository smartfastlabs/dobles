FROM python:3.9-slim-bullseye

# Create folder system for all the code to go
ENV APP_DIR dobles

WORKDIR $APP_DIR

RUN apt-get update && apt-get install -y gcc  && apt-get install -y make

COPY . .


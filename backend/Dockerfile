FROM python:3.11-alpine


ENV DockerHOME=/home/app/backend

# Set work directory
RUN mkdir -p $DockerHOME
RUN mkdir $DockerHOME/staticfiles

# Where your Django project lives on your local system
WORKDIR $DockerHOME

# PREVENT PYTHON FROM WRITING BYTE CODE .pyc
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1  

# Copy the current directory contents into the container at $DockerHOME
COPY .. $DockerHOME

# Install necessary packages on the container
RUN apk update && apk add --no-cache gcc python3-dev musl-dev icu-data-full postgresql-dev gettext

# Install any needed packages specified in requirements.txt and upgrade pip
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r ./requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

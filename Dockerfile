# Use the official Python base image from Docker Hub
FROM python:3.10-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y netcat gcc

# Copy requirements file
COPY ./requirements.txt /app/requirements.txt

# Install python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project
COPY . /app

# Expose port
EXPOSE 8501

# cmd to launch app when container is run
CMD streamlit run app.py

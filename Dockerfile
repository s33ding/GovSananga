# Use the official Python image
#FROM python:3.10-slim
FROM public.ecr.aws/docker/library/python:3.10-slim

ENV AWS_DEFAULT_REGION=us-east-1

# Set working directory
WORKDIR /app

# Install system dependencies (libexpat1 and vim)
RUN apt-get update && apt-get install -y \
    libexpat1 \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code
COPY app/ ./app/

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Streamlit runs on
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "app/main.py"]


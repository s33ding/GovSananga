# Use the official Python image
FROM public.ecr.aws/docker/library/python:3.10-slim

# Set environment variables
ENV AWS_DEFAULT_REGION=us-east-1
ENV AWS_PAGER=""
ENV PATH="/home/appuser/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Install system dependencies and AWS CLI
RUN apt-get update && apt-get install -y \
    libexpat1 \
    vim \
    curl \
    unzip \
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user and switch to it
RUN useradd -ms /bin/bash appuser
USER appuser

# Set working directory for the non-root user
WORKDIR /app

# Copy application code and install Python dependencies
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser requirements.txt .

# Install dependencies locally for appuser
RUN pip install --no-cache-dir --user -r requirements.txt

# Expose Streamlit port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "app/main.py", "--server.baseUrlPath=/govsananga", "--server.enableCORS=false"]


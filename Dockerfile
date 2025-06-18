# Use the official Python image
FROM public.ecr.aws/docker/library/python:3.10-slim

ENV AWS_PAGER=""
ENV PATH="/home/appuser/.local/bin:$PATH"
ENV PYTHONPATH=/app

# Create user before switching
RUN useradd -ms /bin/bash appuser

# Set working directory
WORKDIR /app

COPY app/ ./
COPY requirements.txt .

# Install system dependencies and AWS CLI as root (must be before switching users!)
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

# Set ownership for non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Set working directory again for appuser (optional)
WORKDIR /app

# Install Python dependencies as appuser
RUN pip install --no-cache-dir --user -r requirements.txt

# Expose Streamlit port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.baseUrlPath=/govsananga", "--server.enableCORS=false"]

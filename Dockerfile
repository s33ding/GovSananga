# Use the official Python image
FROM public.ecr.aws/docker/library/python:3.10-slim

ENV AWS_PAGER=""
ENV PATH="/home/appuser/.local/bin:$PATH"
ENV PYTHONPATH=/app


RUN useradd -ms /bin/bash appuser

# Set working directory
WORKDIR /app

COPY app/ ./app/
COPY requirements.txt .

# Set ownership while still root
RUN chown -R appuser:appuser /app

# Now switch to non-root user
USER appuser

# Set working directory again for appuser (optional, for clarity)
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

# Install dependencies locally for appuser
RUN pip install --no-cache-dir --user -r requirements.txt
# Set working directory
WORKDIR /app

# Expose Streamlit port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "app/main.py", "--server.baseUrlPath=/govsananga", "--server.enableCORS=false"]

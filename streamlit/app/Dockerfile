# Use a lightweight Python base image
FROM python:3.12-alpine

# Set the working directory inside the container
WORKDIR /app

RUN apk add --no-cache \
    gcc \
    musl-dev \
    gdal-dev \
    geos-dev \
    proj-dev \
    proj \
    libffi-dev \
    build-base \
    python3-dev \
    jpeg-dev \
    zlib-dev

# Copy the application files
COPY app/ .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Specify the command to run your app
CMD ["python", "app.py"]


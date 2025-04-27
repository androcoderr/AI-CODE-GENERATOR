# Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install netcat to use for service availability check
RUN apt-get update && apt-get install -y netcat

# Copy application
COPY app/ .

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "main.py"]

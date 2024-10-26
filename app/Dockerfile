# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3-dev \
    default-libmysqlclient-dev \
    gcc \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Copy the entrypoint script
COPY entrypoint.sh /app/entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Expose the port on which Django will run
EXPOSE 8000

# Set entrypoint to the entrypoint.sh script
ENTRYPOINT ["/app/entrypoint.sh"]

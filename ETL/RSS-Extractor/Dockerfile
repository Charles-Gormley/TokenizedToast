# We start from a base image that already has Python installed
FROM python:3.8-slim-buster

# Create a working directory
WORKDIR /app

# Copy requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# This command will be run when the container starts
CMD ["python", "main.py"]

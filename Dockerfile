# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory to /app inside the container
WORKDIR /app

# # Copy the directory src an data into the filesystem at /app in the container
# COPY src/ .
# COPY data/ .

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Run the main script when the container launches
CMD ["python", "main.py"]

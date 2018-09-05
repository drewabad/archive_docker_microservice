# Use an official Python runtime as a parent image
FROM python:3-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8002 available to the world outside this container
# EXPOSE 8002

# Define environment variable
ENV NAME TransactionAPI

# Run app.py when the container launches
CMD ["python", "transaction_api.py"]
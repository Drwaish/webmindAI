FROM python:3.12.0-slim

# Set the working directory
WORKDIR /app

# Copy only the requirements file first (for better caching)
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Set environment variables from the .env file
# Docker Compose or the `--env-file` flag should be used to pass the .env file

# Expose necessary port (change as per application needs)
EXPOSE 5000

# Define the command to run the application
CMD ["python", "app.py"]

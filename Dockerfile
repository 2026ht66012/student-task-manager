# Use lightweight official Python image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and assets
COPY . .

# Expose the Flask port
EXPOSE 5000

# Define command to run the application
CMD ["python", "app.py"]

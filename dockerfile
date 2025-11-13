# Start from the official Python 3.10 slim image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the main application file
COPY main.py .

# The 'storage' directory will be created by the app at runtime
# main.py contains: STORAGE_DIR.mkdir(exist_ok=True)

# Expose the port the app will run on
EXPOSE 8000

# The command to run when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
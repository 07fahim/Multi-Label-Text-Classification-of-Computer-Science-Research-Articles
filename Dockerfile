# Use a lightweight Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the files
COPY . .

# Expose the port Render expects
EXPOSE 10000

# Run with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]

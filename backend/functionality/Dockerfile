FROM python:3.11

# Set working directory
WORKDIR functionality

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose the port your app runs on
EXPOSE 5001

# Run the app
CMD ["python3", "app.py"]
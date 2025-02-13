# Base image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Copy main application files
COPY manage.py /app/
COPY core /app/core/
COPY app /app/app/
COPY entrypoint.sh /entrypoint.sh

# Copy RAG project
COPY RAG /app/RAG/

# Copy the single requirements.txt file
COPY requirements.txt /app/requirements.txt

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Make entrypoint executable
RUN chmod +x /entrypoint.sh

# Expose the application port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

# Base image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

COPY . .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1

# Expose the application port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]

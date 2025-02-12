# Base image
FROM python:3.10

# Set the working directory in the container
WORKDIR /app

# Copy main application files
COPY manage.py /app/
COPY core /app/core/
COPY app /app/app/
COPY entrypoint.sh /entrypoint.sh

# Copy CompletedRAG project
COPY CompletedRAG /app/CompletedRAG/

# Combine requirements.txt from both locations
COPY requirements.txt /app/requirements_main.txt
COPY CompletedRAG/requirements.txt /app/requirements_rag.txt

# Install dependencies from both requirements files
RUN pip install --no-cache-dir -r requirements_main.txt \
    && pip install --no-cache-dir -r requirements_rag.txt

# Make entrypoint executable
RUN chmod +x /entrypoint.sh

# Expose the application port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

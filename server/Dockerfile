FROM python:3.10-slim

WORKDIR /app

COPY server.py config.json /app/

# Expose the server port
EXPOSE 5000

# Run the server
CMD ["python", "-u", "server.py"]

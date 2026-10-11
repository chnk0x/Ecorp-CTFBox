FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir flask
COPY app.py .
COPY templates/ templates/
COPY evidence/ evidence/
RUN useradd -m ctf
USER ctf
EXPOSE 8080
CMD ["python", "app.py"]

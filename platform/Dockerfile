FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir flask
COPY app.py index.html seed_flags.py ./
COPY artefacts/ artefacts/
RUN python seed_flags.py && rm seed_flags.py && useradd -m ctf && chown -R ctf /app
USER ctf
ENV HOST=0.0.0.0
EXPOSE 5000
CMD ["python", "app.py"]

FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install .

EXPOSE 7860

CMD ["python", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
FROM python:3.10.14-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
EXPOSE 3002
CMD ["python", "index.py"]

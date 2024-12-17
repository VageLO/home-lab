FROM python:3.12
WORKDIR /api
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ./ .
CMD ["fastapi", "run", "./main.py"]

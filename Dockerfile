FROM python:3.13-alpine

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY mmwave_vis/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mmwave_vis/ .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh && mkdir -p /data

EXPOSE 5000

CMD ["./entrypoint.sh"]

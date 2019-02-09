FROM arm32v7/python:3.7.2-slim-stretch

RUN pip install --no-cache-dir -r /usr/deploy/src/requirements.txt
RUN pip install gpiozero
RUN pip install gunicorn

# Start gunicorn
CMD ["gunicorn","-w", "4", "-b", "0.0.0.0:8000", "app:app"]

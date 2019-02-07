FROM raspbian/stretch

# Setup flask application
RUN mkdir -p /deploy/src
COPY src /deploy/src
RUN pip3 install -r /deploy/src/requirements.txt
RUN pip3 install gunicorn
WORKDIR /deploy/src

# Start gunicorn
CMD ["gunicorn","-w", "4", "-b", "0.0.0.0:8000", "app:app"]

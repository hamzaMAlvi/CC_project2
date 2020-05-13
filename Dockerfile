FROM python:3.8
COPY flaskApp /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD [ "python", "flaskApp.py" ]
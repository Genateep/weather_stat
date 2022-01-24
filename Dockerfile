FROM python:3

WORKDIR /weather_stat

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD [ "python3", "weather_stat/manage.py", "runserver", "0.0.0.0:8000"]
   Django app that gives weather statistics from 2010-01-01 for 15 cities.
Has a database from 01-01-2010 to 01-24-2022.
Keep in mind that script updates database on first request, which may take some time.

   To run the app use command line
   
	>>>python manage.py runserver
and then go to http://localhost:8000


   To run with docker:
   
	>>>docker-compose up
or pull it from hub.docker.com

	>>>docker pull genateep/weather_stat
	>>>docker run --publish 8000:8000 weather_stat

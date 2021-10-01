# Teacher-Directory-App

**Prepare**

•	Download and Install Python Here required python version 3.8.x https://www.python.org/downloads/

•	Install django and start new project inside your directory according the above structure

   	pip install django

   	django-admin startproject main.

•	Create new app app/ to store the collection

   	python manage.py startapp app

 Register your app in the main project, the app to INSTALLED_APP in settings.py
 
•	 make migrations into db.sqlite3 (database) to create the table for the new model

	python manage.py makemigrations

   	python manage.py migrate

**How to Run**

•	Move all of this files to django folder project (replace it)

•	open your command line and type 
	
	python manage.py runserver

•	open your browser and type URL http://127.0.0.1:8000/


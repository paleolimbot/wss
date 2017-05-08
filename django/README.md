# Water Safety Surveys Django Project

This folder contains a 'django project', which implements the `wss` Django app contained within. 

To setup the project, install the dependencies (this project uses Python 3):

```
pip3 install django
pip3 install django-nested-admin
```

Then create the database:

```
python3 manage.py migrate
```

Then create the super admin user:

```
python3 manage.py createsuperuser
```

To run the project, type:

```
python3 manage.py runserver
```

If the server starts properly, you can direct your browser to http://127.0.0.1:8000/admin to enter the free administrator utility.
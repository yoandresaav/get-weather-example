
### Create python virtual environment [In this case .venv is the name I prefer but could be other]
```cmd
python -m venv .venv
```

### Activate python virtual environment
```cmd
source .venv/bin/activate
```

### Create .env file
Copy .env.test to .env and provide real values

### Install packages
```cmd
pip install -r requirements.txt
```

### Run migrations
```cmd
python manage.py migrate
```

### Create super user (admin login)
```cmd
python manage.py createsuperuser
```

### Run server
```cmd
python manage.py runserver
```

### Open in browser
Open localhost:8000 or click in this [link](http://localhost:8000)

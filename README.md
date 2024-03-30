
## Introduction

Clone this repo. You will need set a weather map api key in order to run correctly this repo.

### Create python virtual environment. Tested in python 3.11 [In this case .venv is the name I prefer but could be other]
```cmd
python -m venv .venv
```

### Activate python virtual environment
```cmd
source .venv/bin/activate
```

### Create .env file
Copy .env.test to .env and provide real values to OPEN_WEATHERMAP_KEY

### Install packages
```cmd
pip install -r requirements.txt
```

### Run migrations
```cmd
python manage.py migrate
```

### Run server
```cmd
python manage.py runserver
```

### Open in browser
Open localhost:8000/?city=mex or click in this [link](http://localhost:8000/?city=mex)


### To run tests, in console run
```cmd
pytest .
```


### Image
![image](relative%20images/screencapture.png?raw=true "Image")

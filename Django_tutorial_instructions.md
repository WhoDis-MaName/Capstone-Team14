# Django Tutorial instructions

## Setup Environment

### Create venv

`python -m venv {environment name}`

### Start venv

`{environment name}/Scripts/activate`

**Note** must enable script running via powershell command `Set-ExecutionPolicy -ExecutionPolicy AllSigned -Scope CurrentUser`

### Install Django

`pip install Django`

### Start Django project

`django-admin startproject {project name}`

### Create Django app

```{bash}
cd {django project name}
python3 manage.py startapp {app name}
```

### Run Django Project

`python manage.py runserver`

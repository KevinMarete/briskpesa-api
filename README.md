BriskPesa
====================================

Setup:
------

`pip install -r requirements.txt`

Usage:
------

- Run server locally: `python manage.py runserver`

- Deploy initial version: `ansible-playbook -i hosts provision.yml`

- Deploy new version: `ansible-playbook -i hosts deploy.yml`
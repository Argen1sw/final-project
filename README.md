# EnviroAlerts - FP

> **Note:** Please refer to the Project Development Environments Configuration for system requirements before deploying the web application.

## Prerequisites

- **Python:** Ensure Python 3.10 is installed.
- **pip:** Ensure pip is installed.
- **Redis:** Required for the asynchronous message broker.
- **Celery:** For task management.

## Steps to Run the Application:

1. Clone the Project Repository:
```
git clone https://github.com/Argen1sw/final-project.git
```
4. Set Up a Virtual Environment:
```
   python3.10 -m venv deployment_env
```
5. Activate the Virtual Environment:

```
source deployment_env/bin/activate
```

5. Navigate to the Project Root Directory: cd final-project

6. Install Required Packages:
```
   pip install -r requirements.txt
```
7. Set Up Redis (Async Message Broker):
  ```
     sudo apt install redis-server
     sudo systemctl start redis-server
     sudo systemctl enable redis-server
     sudo systemctl status redis-server
  ```

8. Start Celery Worker and Beat: (Use two separate terminals)
```
  Terminal 1 - Worker: celery -A enviroAlerts worker -l info
  Terminal 2 - Beat: celery -A enviroAlerts beat -l info
```
10. Run Project Tests:
```
    python manage.py test
```
12. Run the Django Web Application: python manage.py runserver

```bash
git clone https://github.com/Argen1sw/final-project.git
```

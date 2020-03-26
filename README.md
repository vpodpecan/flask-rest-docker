## Flask REST API skeleton with dockerized Flask + flask_restx, Postgres, SQLAlchemy, Gunicorn, Nginx, Celery, Flower and Redis


This repository extends [flask-on-docker](https://github.com/testdrivenio/flask-on-docker) with Celery, Redis and Flask_restx to provide a skeleton for building dockerized Flask RESTful APIs.

### Requirements
-  docker
-  docker-compose

### How to use

The code is ready to be tested without additional configuration. However, it is strongly recommended that you modify `.env.prod` and change Postgres and Flower user and password data before moving the code into production.

The functions that define the API reside in `services/web/project/__init__.py`. They call functions `services/web/project/api_functions.py` to do the computation. Asynchronous functions which are handled by Celery reside in `services/celery-queue/tasks.py`.

The skeleton provides few examples of synchronous and asynchronous functions which can serve as templates for implementing your own.
In short, you need to:

1.  Define the API call in `services/web/project/__init__.py` by writing a `Resource` class with the appropriate methods (e.g., get and post), decorate the class and the methods to get automated documentation and testing.
2. Implement the actual function in `services/web/project/api_functions.py`. If the function is asynchronous, write also a handler in `services/celery-queue/tasks.py`. Results of asynchronous functions are stored in Redis which is configured to be persistent.

#### Development

The following command

```sh
$ docker-compose up -d --build
```

will build the images and run the containers. If you go to [http://localhost:5000](http://localhost:5000) you will see a web interface where you can check and test your REST API. Flower monitor for Celery is running on [http://localhost:5555](http://localhost:5555). Note that the `web` folder is mounted into the container and the Flask development server reloads your code automatically so any changes will be visible immediately.

#### Production

The following command

```sh
$ docker-compose -f docker-compose.prod.yml up -d --build
```

will build the images and run the containers. The web interface is now available at [http://localhost](http://localhost) and the Flower monitor at [http://localhost:5555](http://localhost:5555). If you change the source code, you will have to do a rebuild for changes to take effect.

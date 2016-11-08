# Django Poll Tutorial

This code was written following the [Official Django Tutorial](https://docs.djangoproject.com/en/1.10/intro/tutorial01/).

## Running the Web Server

The included Dockerfile is built to launch the built in Django web server, running on localhost port 8000.

``` bash
$ docker build -t django_poll_tutorial .
$ docker run -d -p 8000:8000 django_poll_tutorial
```

### Developing

``` bash
$ docker run --name django_poll_tutorial -it -p 8000:8000 -v $(pwd)/app:/home/app django_poll_tutorial
```

Now you can edit the code in /app from outside the container with your favorite editor.
To execute further commands inside the running container:

``` bash
$ docker exec -it django_poll_tutorial bash
```

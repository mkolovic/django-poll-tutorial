FROM python:3.5.1

ENV PORT 8000
EXPOSE $PORT

RUN pip install Django==1.10.3
RUN mkdir -p /home/app
COPY ./app /home/app

WORKDIR /home/app

CMD python manage.py runserver 0.0.0.0:$PORT

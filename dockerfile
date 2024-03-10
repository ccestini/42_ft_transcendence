FROM python:3.9

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/
RUN apt-get update && apt-get install -y dos2unix

RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install django-crispy-forms \
    && pip install crispy-bootstrap4 \
    && pip install requests \
    && pip install psycopg2-binary \
    && pip install django-cors-headers \
	&& pip install django-debug-toolbar \
	&& pip install django-sslserver \
    && pip install djangorestframework\
    && pip install django-otp \
    && pip install pyotp \
    && pip install rest_framework_simplejwt \
    && pip install djangorestframework-simplejwt[crypto]

COPY migrate.sh /code/migrate.sh

RUN chmod +x /code/migrate.sh

COPY . /code/
COPY .env /code/.env

RUN rm -rf /code/migrations

RUN dos2unix /code/migrate.sh

CMD ["bash", "migrate.sh"]

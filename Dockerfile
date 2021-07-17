FROM python:3.8

WORKDIR /scrapping-app-with-restapi

ADD . /scrapping-app-with-restapi

RUN pip install -r requirements.txt

# CMD ["python", "wsgi.py"]
EXPOSE 5000
CMD ["gunicorn", "-b0.0.0.0:8000" , "wsgi:app"]
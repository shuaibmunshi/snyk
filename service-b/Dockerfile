FROM python

RUN apt-get update && apt-get -y install dnsutils

WORKDIR /app

COPY requirements.txt ./
COPY app.py ./
RUN pip3 install -r requirements.txt

EXPOSE 5000

ENV FLASK_APP=app.py

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
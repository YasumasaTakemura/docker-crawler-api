FROM ubuntu

RUN apt update && \
    apt install --yes python3 python3-pip && \
    apt clean && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    ln -s /usr/bin/pip3 /usr/bin/pip

# crawler application
COPY ./ /src

# python
RUN pip install -r /src/requirements.txt

# uwsgi
RUN touch /src/reload.trigger && \
    if [ ! -d "/var/log/uwsgi" ] ; then mkdir /var/log/uwsgi ; fi

WORKDIR /src

RUN ls app

EXPOSE 80 8080

CMD ["uwsgi","--ini","uwsgi.ini"]
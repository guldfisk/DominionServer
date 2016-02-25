# DOCKER-VERSION 1.1.2
FROM python
MAINTAINER Oliver Nybroe <olivernybroe@gmail.com>

VOLUME ["/data"]
EXPOSE 6700

ADD * /tmp/
RUN chmod 755 -R /tmp/

CMD ["pip", "install numpy"]

CMD ["python", "/tmp/domServer.py"]
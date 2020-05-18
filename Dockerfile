FROM python:3.6.10
ENV PYTHONUNBUFFERED 1
ENV C_FORCE_ROOT true
RUN mkdir ~/.pip
COPY config/pip.conf ~/.pip/pip.conf
RUN mkdir home/src
RUN mkdir /static
ADD requirements.txt /home/requirements.txt
RUN pip install -r /home/requirements.txt
WORKDIR /home/src
ADD . /home/src
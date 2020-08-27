FROM python:3.6.10
ENV PYTHONUNBUFFERED 1
ENV C_FORCE_ROOT true
RUN mkdir ~/.pip
COPY config/pip.conf ~/.pip/pip.conf
RUN mkdir home/knu_notice
RUN mkdir /static
ADD config/requirements.txt /home/config/requirements.txt
RUN pip install -r /home/config/requirements.txt
WORKDIR /home/knu_notice
ADD . /home/knu_notice
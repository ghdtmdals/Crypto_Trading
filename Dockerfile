FROM python:3.12-slim-bookworm

RUN pip install sqlalchemy pymysql pandas scikit-learn

RUN apt-get update && apt-get install -y sudo

RUN adduser --disabled-password --gecos "" user  \
        && echo 'user:user' | chpasswd \
        && adduser user sudo \
        && echo 'user ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN sudo apt-get install -y nano cron systemd
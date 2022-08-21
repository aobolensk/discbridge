FROM python:3.10

WORKDIR /discbridge
ADD . /discbridge

RUN apt-get update
RUN apt-get install -y libolm-dev python3-olm
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

CMD ["python", "discbridge.py"]

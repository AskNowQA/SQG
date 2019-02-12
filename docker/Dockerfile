FROM python:3.7

RUN echo 'deb http://httpredir.debian.org/debian jessie-backports main' > /etc/apt/sources.list.d/jessie-backports.list
RUN apt-get update
RUN apt-get install -y python-gevent python-gevent-websocket emacs

WORKDIR /data/hamid/workspace
RUN git clone https://github.com/AskNowQA/SQG.git
WORKDIR /data/hamid/workspace/SQG
RUN git checkout dev && git pull origin dev
COPY ./data /data/hamid/workspace/SQG/data
RUN pip install --upgrade pip
RUN pip install Cython
RUN pip install https://download.pytorch.org/whl/cpu/torch-1.0.1-cp37-cp37m-linux_x86_64.whl
RUN pip install torchvision
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=.:$PYTHONPATH
CMD ["python", "sqg_webserver.py", "--port", "5005" ]
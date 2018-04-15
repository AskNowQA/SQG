FROM python:2.7.14
COPY ./docker/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD [ "python", "./sqg_webserver.py", "--port", "5000" ]
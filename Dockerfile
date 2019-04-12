FROM python:3.6.5

RUN mkdir /usr/src/build
WORKDIR /usr/src/build

COPY . .

RUN pip install -e .
RUN pip install -e .[dev]

CMD tail -f /dev/null
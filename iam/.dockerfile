FROM python:3.14.3-trixie as core

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/presentation/generated:${PYTHONPATH}"

COPY ./requirements.txt /tmp/requirements.txt

RUN pip install --upgrade pip ; pip install uv
RUN uv pip install --system -r /tmp/requirements.txt
COPY . /app

FROM core as test_extended

COPY ./tests/tests.requirements.txt /tmp/
RUN uv pip install --system -r /tmp/tests.requirements.txt


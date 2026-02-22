FROM python:3.12

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/usr/src/app/src

LABEL org.opencontainers.image.title="music_app"
LABEL org.opencontainers.image.description="Docker image for the Music App FastAPI project"

COPY ./database /usr/src/app/database
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --upgrade pip && \
    pip install -r /usr/src/app/requirements.txt

COPY . /usr/src/app/

EXPOSE 8001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]

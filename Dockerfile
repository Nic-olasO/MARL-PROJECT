FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONPATH=/workspace/src
ENV PYGAME_HIDE_SUPPORT_PROMPT=1

WORKDIR /workspace

COPY requirements-docker.txt .
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements-docker.txt

COPY . .

CMD ["python", "src/marl_sim/smoke_pettingzoo.py"]

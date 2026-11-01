FROM python:3.13-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /opt/still-water
COPY requirements-m2.txt ./
RUN pip install --no-cache-dir -r requirements-m2.txt
COPY tools/ ./tools/
CMD ["python", "tools/pi_bridge.py"]

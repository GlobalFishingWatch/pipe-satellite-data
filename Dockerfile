FROM python:3.12-slim-bookworm AS base

# Update system and install build tools. Remove unneeded stuff afterwards.
# Upgrade PIP.
# Create working directory.
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ build-essential && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip && \
    mkdir -p /opt/project

# Set working directory.
WORKDIR /opt/project

# RUN apt-get -y install gdal-bin libgdal-dev

# Setup scheduler-specific dependencies
COPY ./requirements.txt ./
RUN pip install -r requirements.txt

# Setup local package
COPY . /opt/project
RUN pip install --no-deps -e .

# Setup the entrypoint for quickly executing the pipelines
ENTRYPOINT ["./main.py"]

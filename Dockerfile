FROM gcr.io/world-fishing-827/github.com/globalfishingwatch/gfw-pipeline:latest-python3.8

RUN apt-get -y install gdal-bin libgdal-dev

# Setup scheduler-specific dependencies
COPY ./requirements.txt ./
RUN pip install -r requirements.txt

# Setup local package
COPY . /opt/project
RUN pip install -e .

# Setup the entrypoint for quickly executing the pipelines
ENTRYPOINT ["./main.py"]

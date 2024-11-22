FROM docker.io/library/python:3.13-slim AS build

RUN mkdir -p /app
WORKDIR /app
# if I copy them explicitly, it does less rebuilding when I change the Dockerfile
COPY mr_radar/ /app/mr_radar
COPY pyproject.toml /app/

# Install build and installer tools
RUN python -m pip install build
# Build the project
RUN cd /app && ls -l && python -m build

FROM docker.io/library/python:3.13-slim
RUN apt update \
    && apt install -y gcc g++ gfortran libopenblas-dev liblapack-dev pkg-config
RUN mkdir /app
COPY --from=build /app/dist/*.whl /app

# Install the built package
RUN cd /app && ls -l &&  \
    python -m pip install /app/MrRadar-0.1.0-py3-none-any.whl

# Show installed packages for debugging
RUN python -m pip list

# Check that mr_radar command is available
RUN which mr_radar

# Test mr_radar command
RUN mr_radar --help

# Ensure we get the extended 256-color pallet when running with `-t`
ENV TERM=xterm-256color

ENTRYPOINT [ "mr_radar" ]
CMD ["--help"]

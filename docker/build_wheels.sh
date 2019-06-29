#!/bin/bash

nvidia-docker run --rm \
    -v $PWD:/pynvvl \
    -t mitmul/pynvvl:cuda-10.1 \
    rm -rf \
    /pynvvl/build \
    /pynvvl/dist \
    /pynvvl/docker/lib \
    /pynvvl/pynvvl*.egg-info
bash docker/build_docker.sh
bash docker/build_nvvl.sh
python docker/build_wheels.py

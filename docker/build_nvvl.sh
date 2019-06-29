#!/bin/bash

build_libnvvl() {
    nvidia-docker run \
    --rm \
    -v $PWD/docker:/root/build -t mitmul/pynvvl:cuda-$1 \
    bash -c " \
    if [ ! -f /usr/local/lib/libnvcuvid.so ]; then \
        ln -s /usr/lib/x86_64-linux-gnu/libnvcuvid.so.1 /usr/local/lib/libnvcuvid.so; \
    fi && \
    rm -rf /root/build/lib/cuda-$1 && \
    mkdir -p /root/build/lib/cuda-$1 && \
    cp -r /usr/local/lib /root/build/lib/cuda-$1 && \
    mv /root/build/lib/cuda-$1/lib/* /root/build/lib/cuda-$1/ && \
    rm -rf /root/build/lib/cuda-$1/lib && \
    cd /root/nvvl && mkdir build && cd build && \
    cd /root/nvvl/build && \
    cmake ../ \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_BUILD_WITH_INSTALL_RPATH=ON \
    -DCMAKE_INSTALL_RPATH=\"\\\$ORIGIN\" && \
    make -j && cp libnvvl.so /root/build/lib/cuda-$1 && \
    apt-get install chrpath && \
    chrpath -l libnvvl.so && \
    cp -r /root/nvvl/include /root/build/"
}

build_libnvvl 10.1

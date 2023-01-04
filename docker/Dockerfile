FROM pytorch/pytorch:1.12.0-cuda11.3-cudnn8-runtime
WORKDIR /home/plate-engine

RUN apt update && apt install -y libsm6 libxext6 libxrender1 git build-essential cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev python-dev libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libdc1394-22-dev libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev gstreamer1.0-libav gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer-1.0 gstreamer1.0-tools git-lfs

RUN apt-get install -y python3
RUN apt-get install -y python3-pip && pip3 install --upgrade pip

COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt
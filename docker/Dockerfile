FROM continuumio/anaconda3
WORKDIR /home/opencv
RUN conda install jupyter -y --quiet && mkdir /home/opencv -p
RUN apt-get update && apt-get install libgl1 -y
RUN pip install opencv-python
EXPOSE 8888

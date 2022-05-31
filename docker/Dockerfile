FROM continuumio/anaconda3
WORKDIR /home/opencv
RUN conda install jupyter -y --quiet && mkdir /home/opencv -p
RUN pip install opencv-python
EXPOSE 8888

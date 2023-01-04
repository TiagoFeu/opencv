from video_capture import RealtimeCapture
from video_buffer import VideoBuffer

import multiprocessing
import time

if __name__ == "__main__":
    context_camera = RealtimeCapture('rtsp://admin:StartID0176@10.50.30.63:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')

    video_buffer = VideoBuffer(context_camera.get_fps(), 10)

    for i in range(100):
        frame, vid_timestamp, cap_time = context_camera.get()
        video_buffer.add_frame(frame)

        print(i, vid_timestamp, cap_time)

# get a frame from video_buffer

frames = video_buffer.get_frames()
print(frames)

print('fim')
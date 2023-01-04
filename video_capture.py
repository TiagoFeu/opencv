import cv2
from threading import Thread, Condition
from datetime import datetime

class RealtimeCapture:
    def __init__(self, video, realtime=True):
        self.video = video
        self.frame = None
        self.timestamp = None
        self.capture_time = None
        self.running = True
        self.fps = None
        self.live_fps = None
        self.discarded_frames = 0
        self.cond = Condition()
        self.fps_cond = Condition()
        self.realtime = realtime
        self.thread = Thread(target=self._cap_thread)
        self.thread.start()

    def _cap_thread(self):
        cap = cv2.VideoCapture(self.video)
        self._set_fps(cap.get(cv2.CAP_PROP_FPS))
        fps_calc_time = datetime.now()
        fps_calc_count = 0

        while self.running:
            ret, frame = cap.read()
            ts = cap.get(cv2.CAP_PROP_POS_MSEC)

            if not ret:
                cap.release()
                cap = cv2.VideoCapture(self.video)
                self._set_fps(cap.get(cv2.CAP_PROP_FPS))
            else:
                with self.cond:
                    if not self.realtime:
                        while self.frame is not None:
                            self.cond.wait()
                    else:
                        if self.frame is not None:
                            self.discarded_frames += 1
                    self.frame = frame
                    self.timestamp = ts
                    self.capture_time = datetime.now()
                    
                    diff = self.capture_time - fps_calc_time
                    if diff.seconds >= 1:
                        secs = float(diff.seconds) + float(diff.microseconds)/1e6
                        self.live_fps = fps_calc_count/secs
                        fps_calc_count = 0
                        fps_calc_time = self.capture_time
                    else:
                        fps_calc_count += 1

                    self.cond.notify()

        cap.release()

    def _set_fps(self, fps: float):
        with self.fps_cond:
            self.fps = fps
            self.fps_cond.notify()
    
    def get_fps(self):
        with self.fps_cond:
            while self.fps is None:
                self.fps_cond.wait()
        
        return self.fps

    def get(self):
        with self.cond:
            while self.frame is None:
                self.cond.wait()
            
            frame = self.frame
            timestamp = self.timestamp
            cap_time = self.capture_time
            self.frame = None
            self.timestamp = None
            self.capture_time = None

            if not self.realtime:
                self.cond.notify()
        
        return frame, timestamp, cap_time

    def close(self):
        with self.cond:
            self.frame = None
            self.timestamp = None
            self.capture_time = None
            self.running = False
            self.cond.notify()
        
        self.thread.join()
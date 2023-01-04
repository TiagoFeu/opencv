from typing import List, Callable, Optional, Tuple, Any
from threading import Thread, Lock
from datetime import datetime
import numpy as np
from yolo import YOLODetection
from speed_estimation import SpeedCalculator
from tracking import PlateTracker, CompleteDetection, SimpleNoLicensePlateTracker
from entities import Color, GeoLocation, OperatingMode
from traffic_light import TrafficLight, LightState
from video_buffer import VideoBuffer
from video_capture import RealtimeCapture
from text_writer import TextWriter
from context_tracking import ContextTracker, ForbiddenPathDetection

class Stream:
    """Stream de video. Esta classe lança uma thread responsável por ler
    e decodificar os dados vindos da stream e colocá-los em uma fila."""
    def __init__(self, application: 'LPR', stream_id: str,
                 url: str,
                 context_url: Optional[str],
                 realtime: bool,
                 buffer_duration: int,
                 on_decode: Callable[[Any], None],
                 on_detect: Callable[[CompleteDetection], None],
                 on_forbidden_path: Callable[[ForbiddenPathDetection], None]) -> None:
        self.application = application
        self.stream_id = stream_id
        self.url = url
        self.context_url = context_url
        self.op_mode = OperatingMode.MOTION
        self.trigger_mode_counter = 0
        self.traffic_light = None
        self.on_decode = on_decode
        self.plate_tracker = PlateTracker(self, on_detect)
        self.no_plate_tracker = SimpleNoLicensePlateTracker(self, on_detect)
        self.context_tracker = ContextTracker(self, on_forbidden_path)
        self.image_quality = 95
        self.video_bitrate = 2048
        self.geolocation = None
        self.perspective = None
        self.video_buffer = None
        self.buffer_duration = buffer_duration
        self.lanes = None
        self.crosswalks = None
        self.roi = None
        self.current_frame = 0
        self.total_plates = 0
        self.streaming_camera = False
        self.streaming_context = False
        self.imshowing = False
        self.running = True
        self.sort_last_frame = -1
        self.sort_pending_frames = []
        self.motion_previous_frame = None
        self.no_license_plate_frames = 0
        self.thread = None
        self.lock = Lock()
        self.cap = RealtimeCapture(self.url, realtime)
        self.context_cap = RealtimeCapture(self.context_url) if self.context_url is not None else None

    def start(self):
        self.running = True
        self.thread = Thread(target=self._decode_thread)
        self.thread.start()
    
    def stop(self):
        self.running = False
        self.thread.join()
        self.thread = None

    def _decode_thread(self):
        self.video_buffer = VideoBuffer(self.context_cap.get_fps(), self.buffer_duration if self.buffer_duration is not None else 5) if self.context_url is not None else None

        while self.running:
            frame, vid_timestamp, cap_time = self.cap.get()
            frame, vid_timestamp, cap_time = self.cap.get()

            if self.context_url is not None:
                ctx_frame, _, _ = self.context_cap.get()
                ctx_frame, _, _ = self.context_cap.get()
                self.video_buffer.add_frame(ctx_frame)
            else:
                ctx_frame = None

            self.on_decode(Frame(self, self.current_frame, frame, ctx_frame, vid_timestamp, cap_time))
            self.current_frame += 1
        
        self.cap.close()

        if self.context_cap:
            self.context_cap.close()
    
    def get_context_fps(self):
        return self.context_cap.get_fps()
    
    def get_lpr_fps(self):
        return self.cap.get_fps()
    
    def get_lpr_live_fps(self):
        return self.cap.live_fps
    
    def get_context_live_fps(self):
        return self.context_cap.live_fps

    def set_op_mode(self, mode: OperatingMode):
        self.op_mode = mode
        self.trigger_mode_counter = 0
    
    def trigger(self):
        self.trigger_mode_counter = 10

    def shutdown(self):
        """Encerra execução dessa stream."""
        self.running = False
        self.thread.join()

class Frame:
    """Frame de vídeo passando pela pipeline de processamento."""
    def __init__(self, stream: Stream, number: int, orig_frame: np.array, context_frame: Optional[np.array],
                 timestamp: float, capture_time: datetime,  resize_size: Tuple[int, int] = (416, 416)) -> None:
        self.stream = stream
        self.number = number
        self.orig_frame = orig_frame
        self.context_frame = context_frame
        self.timestamp = timestamp
        self.capture_time = capture_time
        self.resize_size = resize_size

        #Informações que serão preenchidas ao longo do pipeline:
        self.preprocessed = None # type: Optional[np.array]
        self.light_state = None # type: Optional[LightState]
        self.has_motion = None # type: Optional[bool]
        self.vehicle_detections = None # type: Optional[List[VehicleDetection]]
        self.plate_detections = None # type: Optional[List[YOLODetection]]
        self.vehicle_colors = None # type: Optional[List[Color]]

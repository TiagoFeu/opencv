from typing import Optional, Tuple, List, Callable, Any
from threading import RLock
import numpy as np
import cv2

class RenderedVideo:
    def __init__(self, path: str, frames: List[np.array]):
        self.path = path
        self.frames = frames

class BufferAction:
    def __init__(self, head_pos: int, callback: Callable[[List[np.array], Any], None], metadata: Any) -> None:
        self.head_pos = head_pos
        self.callback = callback
        self.metadata = metadata


class VideoBuffer:
    """Armazena os frames mais recentes. Especificamos o fps do vídeo e o número n de segundos de video
    que o buffer deve armazenar. É alocado um buffer com tamanho suficiente para armazenar 2n
    segundos de video. É possível agendar para que um callback seja executado após n segundos
    (isso permite implementar o recurso de gerar um video com n segundos antes e depois de um incidente)"""
    def __init__(self, fps: int = 30, seconds: int = 5) -> None:
        self.num_frames = int(fps*seconds)
        self.buffer_size = int(2*self.num_frames)
        self.buffer = [None]*self.buffer_size
        self.buffer_head = 0
        self.fps = fps
        self.scheduled = [] # type: List[BufferAction]
        self.lock = RLock() # lock impede que o buffer seja alterado enquanto estamos gerando um vídeo
    
    def add_frame(self, frame: np.array) -> None:
        self.lock.acquire()
        self.buffer[self.buffer_head] = frame

        if self.scheduled and self.scheduled[0].head_pos == self.buffer_head:
            sched = self.scheduled.pop(0)
            frames = self.get_frames()
            sched.callback(frames, sched.metadata)

        self.buffer_head = (self.buffer_head + 1)%self.buffer_size
        self.lock.release()
    
    def schedule(self, callback: Callable[[List[np.array], Any], None], metadata: Any) -> None:
        self.lock.acquire()
        head_pos = (self.buffer_head + self.num_frames)%self.buffer_size
        self.scheduled.append(BufferAction(head_pos, callback, metadata))
        self.lock.release()
    
    def get_frames(self) -> List[np.array]:
        self.lock.acquire()
        frames = []
        for i in range(self.buffer_size):
            f = self.buffer[(self.buffer_head+i)%self.buffer_size]

            if f is not None:
                frames.append(f)
        
        self.lock.release()

        return frames

    def resize(self, seconds: int) -> None:
        """ Redimensiona este buffer para armazenar a quantidade especificada de segundos.
        Copia o que for possível do buffer anterior e reajusta os schedules."""
        self.lock.acquire()
        new_num_frames = int(self.fps*seconds)
        new_buffer_size = int(2*new_num_frames)
        new_buffer = [None]*new_buffer_size

        for i in range(1, min(self.buffer_size, new_buffer_size)+1):
            new_buffer[-i%new_buffer_size] = self.buffer[(self.buffer_head-i)%self.buffer_size]
        
        for sched in self.scheduled:
            frames_to_complete = sched.head_pos - self.buffer_head if self.buffer_head <= sched.head_pos else self.buffer_size - self.buffer_head + sched.head_pos
            sched.head_pos = min(frames_to_complete, new_buffer_size-1)
        
        self.num_frames = new_num_frames
        self.buffer_size = new_buffer_size
        self.buffer = new_buffer
        self.buffer_head = 0
        self.lock.release()

    def resize_to_default(self) -> None:
        self.resize(5)

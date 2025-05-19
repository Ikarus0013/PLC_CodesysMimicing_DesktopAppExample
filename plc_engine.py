from dataclasses import dataclass
from typing import Dict, List, Optional
import time
import threading
from datetime import datetime

@dataclass
class IOPoint:
    name: str
    value: bool
    type: str  # 'input' or 'output'
    address: str

class Timer:
    def __init__(self, name: str):
        self.name = name
        self.start_time: Optional[float] = None
        self.preset: float = 0.0
        self.accumulated: float = 0.0
        self.running: bool = False

    def start(self):
        if not self.running:
            self.start_time = time.time()
            self.running = True

    def stop(self):
        if self.running:
            self.accumulated += time.time() - self.start_time
            self.running = False
            self.start_time = None

    def reset(self):
        self.accumulated = 0.0
        self.running = False
        self.start_time = None

    @property
    def elapsed(self) -> float:
        if not self.running:
            return self.accumulated
        return self.accumulated + (time.time() - self.start_time)

class PLCEngine:
    def __init__(self):
        self.inputs: Dict[str, IOPoint] = {}
        self.outputs: Dict[str, IOPoint] = {}
        self.timers: Dict[str, Timer] = {}
        self.counters: Dict[str, int] = {}
        self.running: bool = False
        self.scan_time: float = 0.0
        self._scan_thread: Optional[threading.Thread] = None

    def add_io_point(self, name: str, type: str, address: str):
        point = IOPoint(name=name, value=False, type=type, address=address)
        if type == 'input':
            self.inputs[name] = point
        else:
            self.outputs[name] = point

    def add_timer(self, name: str):
        self.timers[name] = Timer(name)

    def add_counter(self, name: str):
        self.counters[name] = 0

    def set_input(self, name: str, value: bool):
        if name in self.inputs:
            self.inputs[name].value = value

    def get_output(self, name: str) -> bool:
        return self.outputs.get(name, IOPoint(name, False, 'output', '')).value

    def add_analog_input(self, name: str, address: str):
        if not hasattr(self, 'analog_inputs'):
            self.analog_inputs = {}
        self.analog_inputs[name] = {'name': name, 'value': 0.0, 'address': address}

    def add_analog_output(self, name: str, address: str):
        if not hasattr(self, 'analog_outputs'):
            self.analog_outputs = {}
        self.analog_outputs[name] = {'name': name, 'value': 0.0, 'address': address}

    def set_analog_input(self, name: str, value: float):
        if hasattr(self, 'analog_inputs') and name in self.analog_inputs:
            self.analog_inputs[name]['value'] = value

    def get_analog_output(self, name: str) -> float:
        if hasattr(self, 'analog_outputs') and name in self.analog_outputs:
            return self.analog_outputs[name]['value']
        return 0.0

    def start(self):
        if not self.running:
            self.running = True
            self._scan_thread = threading.Thread(target=self._scan_loop)
            self._scan_thread.daemon = True
            self._scan_thread.start()

    def stop(self):
        self.running = False
        if self._scan_thread:
            self._scan_thread.join()

    def _scan_loop(self):
        while self.running:
            start_time = time.time()
            self._execute_scan()
            self.scan_time = time.time() - start_time
            time.sleep(0.01)  # 10ms scan time

    def _execute_scan(self):
        # --- TIMER LOGIC: Y0 turns ON if X0 is ON for 3s ---
        x0 = self.inputs.get('X0', None)
        y0 = self.outputs.get('Y0', None)
        t1 = self.timers.get('T1', None)
        if not hasattr(self, '_last_x0'):
            self._last_x0 = False
        if x0 and y0 and t1:
            # Rising edge: X0 OFF -> ON
            if x0.value and not self._last_x0:
                t1.reset()
                t1.start()
            # While X0 is ON, let timer run
            if not x0.value and self._last_x0:
                t1.stop()
                t1.reset()
                y0.value = False
            if x0.value and t1.elapsed >= 3.0:
                y0.value = True
            self._last_x0 = x0.value
        # --- COUNTER LOGIC: C1 increments on X1 rising edge, Y1 ON if C1 is even ---
        x1 = self.inputs.get('X1', None)
        y1 = self.outputs.get('Y1', None)
        if not hasattr(self, '_last_x1'):
            self._last_x1 = False
        if x1 and y1:
            if x1.value and not self._last_x1:
                self.counters['C1'] += 1
            self._last_x1 = x1.value
            y1.value = (self.counters['C1'] % 2 == 0 and self.counters['C1'] > 0)
        # --- ANALOG LOGIC: AO0 = min(AI0 * 2, 100) ---
        if hasattr(self, 'analog_inputs') and hasattr(self, 'analog_outputs'):
            ai0 = self.analog_inputs.get('AI0', None)
            ao0 = self.analog_outputs.get('AO0', None)
            if ai0 and ao0:
                ao0['value'] = min(ai0['value'] * 2, 100)

    def get_status(self) -> dict:
        status = {
            'inputs': {name: point.value for name, point in self.inputs.items()},
            'outputs': {name: point.value for name, point in self.outputs.items()},
            'timers': {name: timer.elapsed for name, timer in self.timers.items()},
            'counters': self.counters.copy(),
            'scan_time': self.scan_time,
            'running': self.running
        }
        if hasattr(self, 'analog_inputs'):
            status['analog_inputs'] = {name: ai['value'] for name, ai in self.analog_inputs.items()}
        if hasattr(self, 'analog_outputs'):
            status['analog_outputs'] = {name: ao['value'] for name, ao in self.analog_outputs.items()}
        return status 
import os
import sys
import serial
import select
import signal

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

played_loops: int  = 0

def print_usage_and_exit():
    print('Usage: python play.py <serial_device> <wav file>', file=sys.stderr)
    exit(1)


def get_serial(port: str) -> serial.Serial:
    s = serial.Serial()
    s.baudrate = 9600
    s.parity = serial.PARITY_NONE
    s.stopbits = serial.STOPBITS_ONE
    s.bytesize = serial.EIGHTBITS
    s.port = port
    s.timeout = None
    s.write_timeout = None
    return s


def data_ready_on_port(port: serial.Serial):
    return bool(select.select([port.fileno()], [], [], 0)[0])


def wait_for_start_signal(port: str):
    with get_serial(port) as s:
        print('Waiting for a signal to start... ', file=sys.stderr, end='', flush=True)
        while not data_ready_on_port(s):
            pass
        print('OK', file=sys.stderr)

        s.timeout = 1
        s.read(size = 1)
        

def signal_playback_finished(port: str):
    with get_serial(port) as s:
        s.write(bytes(ord('S')))
        s.flush()
        

def playback(recording: str):
    pygame.mixer.init()
    pygame.mixer.music.load(recording)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pass

"""
This utility plays the ACI program wav file. The utility works in an infinite loop:
1. It waits for the signal from the A1SI to begin playback. 
2. After the playback ends, the utility sends a signal via A1SI that the playback has finished.
3. goto 1

This utility requires pyserial and pygame modules to be installed:

pip3 install pyserial
pip3 install pygame
"""
if __name__ == "__main__":

    if len(sys.argv) != 3:
        print_usage_and_exit()

    def print_played_loops_and_exit(status: int):
        print(f'\nPlayed {played_loops} times', file=sys.stderr)
        exit(status)

    # terminate silently on SIGINT
    signal.signal(signal.SIGINT, lambda s, fr: print_played_loops_and_exit(1))

    while True:
        wait_for_start_signal(sys.argv[1])
        playback(sys.argv[2])
        signal_playback_finished(sys.argv[1])
        played_loops += 1

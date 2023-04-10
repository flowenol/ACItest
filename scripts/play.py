import argparse
import os
import sys
import serial
import select
import signal

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

played_loops: int  = 0

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
        

def playback(recording: str, volume: float = 1.0):
    pygame.mixer.init()
    pygame.mixer.music.load(recording)
    pygame.mixer.music.set_volume(volume)
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

    def volume_range_type(arg: int):
        volume = int(arg)
        if volume < 1 or volume > 100:
            raise argparse.ArgumentTypeError(f"Volume: {volume} is not in range [0, 100]")
        return volume

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--device", type=str, required=True, help="path to the serial device")
    argparser.add_argument("--volume", type=volume_range_type, default=100, help="the desired volume level (0-100)")     
    argparser.add_argument("file", type=str, nargs=1, help="path to the program sound file")

    args = argparser.parse_args()

    def print_played_loops_and_exit(status: int):
        print(f'\nPlayed {played_loops} times', file=sys.stderr)
        exit(status)

    # terminate silently on SIGINT
    signal.signal(signal.SIGINT, lambda s, fr: print_played_loops_and_exit(1))

    while True:
        wait_for_start_signal(args.device)
        playback(args.file[0], args.volume / 100.0)
        signal_playback_finished(args.device)
        played_loops += 1

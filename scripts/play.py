import argparse
import os
import sys
import serial
import select
import signal
import threading
import types

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

commands = types.SimpleNamespace()
commands.START_PLAYBACK = b'S'
commands.PLAYBACK_FINISHED = b'S'
commands.VOLUME = b'V'


def get_serial(port: str) -> serial.Serial:
    s = serial.Serial()
    s.baudrate = 9600
    s.parity = serial.PARITY_NONE
    s.stopbits = serial.STOPBITS_ONE
    s.bytesize = serial.EIGHTBITS
    s.port = port
    s.timeout = 1
    s.write_timeout = None
    return s


def data_ready_on_port():
    return bool(select.select([port.fileno()], [], [], 1)[0])

def wait_for_data():
    while not signal_thread_stop.is_set():
        if not data_ready_on_port():
            continue
        
        command = port.read(size = 1)
        match command:
            case commands.START_PLAYBACK:
                with playback_signal_sent:
                    playback_signal_sent.notify_all()
            case commands.VOLUME:
                signal_volume_level()
            case other:
                pass
    
    with signal_thread_stopped:
        signal_thread_stopped.notify_all()


def signal_playback_finished():
    port.write(commands.PLAYBACK_FINISHED)
    port.flush()


def signal_volume_level():
    def volume_level_to_bcd():
        global volume_level
        assert volume_level >= 0 and volume_level <= 100
        return (((int(volume_level / 10) & 0x0f) << 4) | (int(volume_level % 10) & 0x0f)).to_bytes(1, 'little')
            
    port.write(volume_level_to_bcd())
    port.flush()        


def playback(recording: str, volume: float = 1.0):
    pygame.mixer.init()
    pygame.mixer.music.load(recording)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pass


played_loops: int  = 0
port = None
playback_signal_sent = threading.Condition()
signal_thread = threading.Thread(target=wait_for_data, daemon=True)
signal_thread_stop = threading.Event()
signal_thread_stopped = threading.Condition()
volume_level: int = 100

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
        signal_thread_stop.set()
        
        with signal_thread_stopped:
            signal_thread_stopped.wait(1)

        exit(status)

    # terminate silently on SIGINT
    signal.signal(signal.SIGINT, lambda s, fr: print_played_loops_and_exit(1))

    volume_level = args.volume

    with get_serial(args.device) as port:
        
        signal_thread.start()

        while True:
            print('Waiting for a signal to start... ', file=sys.stderr, end='', flush=True)
            with playback_signal_sent:
                playback_signal_sent.wait()
            print('OK', file=sys.stderr)
            playback(args.file[0], volume_level / 100.0)
            signal_playback_finished()
            played_loops += 1

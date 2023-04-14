
# ACItest

Apple-1 Cassette Interface testing utility.

## Description

This repository contains utility which allows you to analyse the reliability of your ACI card over multiple continuous runs. It uses external host (a PC running python script) and [Apple-1 Serial Interface](https://github.com/flowenol/apple1serial) to reliably control the playback routines.

## Requirements

You need the following to successfully build and run the program:

* [xa](https://www.floodgap.com/retrotech/xa/) 6502 cross assembler.
* `python3` with `pyserial` (serial communication) and `pygame` (*.wav playback) modules installed:
```bash
pip3 install pyserial pygame
```

## How to build?

To build the program just type:

`make`

And to clean the build:

`make clean`

There are two output files:

* `acitest-c300.bin` - use if your A1SI card is mapped to `$C300`
* `acitest-c600.bin` - if your A1SI card is mapped to `$C600`

## How to use?

First you have to load the Apple-1 program of your choice to its respective address. The program must be loaded for ACItest to calculate its checksum for later comparisons during test runs.
You can load the program by any mean that is most comfortable to you. Either use the ACI, the A1SI, the [Apple-1 RAM/ROM cartridge](https://github.com/flowenol/apple1cartridge) or others. Just make sure that the loaded program works as intended (especially when you load via ACI).

Then load the ACITest using the same method. ACITest must be loaded at `$0300` to run correctly.

You must initialize the following memory locations:

| address | function |
| --- | --- |
| `$0030` | The number of test runs. |
| `$0034-$0037` | The little-endian ordered bytes of the start and end addresses of the program to be compared during test runs. For example, when using the Integer BASIC for tests, just type: `34: 00 E0 FF EF` in the Wozmon. |

Before you start the ACItest on your Apple-1 you have to start the host script on your PC:

```bash
python3 play.py --volume 100 --device /dev/tty.usbserial-A906METO ~/basic.wav
```
Below is the description the script parameters:
```
usage: play.py [-h] --device DEVICE [--volume VOLUME] file

positional arguments:
  file             path to the program sound file

options:
  -h, --help       show this help message and exit
  --device DEVICE  path to the serial device
  --volume VOLUME  the desired volume level (0-100)
```
Make sure that your host PC system volume is set to 100%. The `--volume` parameter of the script doesn't affect the system volume level and only manipulates the output of the script during playback.

Once the script is started on the host PC, you can start the ACItest on your Apple-1 by typing:`300R` in the Wozmon.
The ACItest should iterate the number of times you specified at the `$0030` memory location. You will be given the result of every playback iteration and the test summary at the end. Type `Ctrl+c` to end the script.

## Playback setup

Just hook up the TAPE IN on the ACI to the audio jack on your PC. Connect the A1SI to the PC as well.

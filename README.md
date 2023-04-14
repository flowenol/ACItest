
# ACItest

Apple-1 Cassette Interface testing utility.

## Description

This repository contains utility which allows you to analyse the reliability of your ACI card over multiple continuous runs. It uses external host (a PC running python script) and [Apple-1 Serial Interface](https://github.com/flowenol/apple1serial) to reliably control the playback routines.

## Requirements

You need the following to successfully build and run the program:

* [xa](https://www.floodgap.com/retrotech/xa/) 6502 cross assembler.
* [GNU Make](https://www.gnu.org/software/make/) utility.
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

Then load the ACItest using the same method. ACItest must be loaded at `$0300` to run correctly.

To load ACItest via ACI or A1SI loader just type:
```
*
300.4E4R
```

After successful load you must initialise the following memory locations:

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

Once the script is started on the host PC, you can start the ACItest on your Apple-1 by typing `300R` in the Wozmon.
The ACItest should iterate the number of times you specified at the `$0030` memory location. You will be given the result of every playback iteration and the test summary at the end. Type `Ctrl+c` to end the script on the host PC.

Example test run:
```
300R

0300: D8
PASS 01
PASS 02
PASS 03
PASS 04
FAIL 05
VOLUME LEVEL: 60
COMPLETED RUNS: 5
PASSED RUNS: 04
FAILED RUNS: 01
```

## Playback setup

Just hook up the TAPE IN on the ACI to the audio jack on the host PC. Connect the A1SI to the PC as well.

## Example test results

I have tested both the ACI of original design (with 100nF input coupling capacitor modification) and the "Improved ACI 2.0" by Uncle Bernie.
The corresponding chips on both ACI boards were of identical origin. The test was run using an Integer BASIC wav file. Each test was run for several volume levels and consisted of 30 playbacks.

#### Improved ACI 2.0

| volume level | passed runs | failed runs | reliability | comment |
| --- | --- | --- | --- | --- |
| 100% | 29 | 1 | 96% | |
| 90% | 29 | 1 | 96% | |
| 80% | 30 | 0 | 100% | |
| 70% | 30 | 0 | 100% | |
| 60% | 30 | 0 | 100% | |
| 50% | 29 | 1 | 96% | |
| 40% | 30 | 0 | 100% | |
| 30% | 30 | 0 | 100% | |
| 25% | 30 | 0 | 100% | |
| 22% | 9 | 21 | 30%  | Intermittent LED glow. |
| 20% | 0 | 30 | 0% | The LED ceased to glow completely. |
| 10% | 0 | 30 | 0% | |

As long as the LED glows the Improved ACI 2.0 is nearly 100% reliable with rare, occasional failed runs.


#### "Original" ACI

| volume level | passed runs | failed runs | reliability | comment |
| --- | --- | --- | --- | --- |
| 100% | 16 | 14 | 53% | The LED doesn't glow and the reliability is poor.|
| 90% | 24 | 6 | 80% | Reliability improves as volume level goes down.|
| 80% | 25 | 5 | 83% | |
| 70% | 26 | 4 | 86% | |
| 60% | 29 | 1 | 96% | |
| 50% | 30 | 0 | 100% | |
| 40% | 19 | 11 | 63% | It starts to decline below 50%. |
| 30% | 0 | 30 | 0% | The ACI becomes very unreliable below 40%. |
| 20% | 0 | 30 | 0% | |
| 10% | 0 | 30 | 0% | |

The "Original" ACI has a sweet spot for volume level between 50% and 60%. The 100% volume level surprisingly yields only 50% reliability, which improves as the volume level gets lower.

### Conclusion

Go with the "Improved ACI 2.0" if you want better reliability. It has a much wider margin of tolerance when loading programs from digital media.

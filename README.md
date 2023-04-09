
# ACItest

Apple-1 Cassette Interface testing utility.

## Description

This repository contains utility which allows you to analyse the reliability of your ACI card over multiple continuous runs. It uses external host and [Apple-1 Serial Interface](https://github.com/flowenol/apple1serial) to control the playback iterations.

## Requirements

You need the following to successfully build and run the program:

* [xa](https://www.floodgap.com/retrotech/xa/) cross assembler.
* `python3` with `pyserial` (serial communication) and `pygame` (*.wav playback) modules installed:
```bash
pip3 install pyserial pygame
```

## How to build?

To build the program just type:

`make`

And to clean the build:

`make clean`

#!/usr/bin/env bash

set -e

sudo apt-get update --fix-missing
sudo apt-get install libudev-dev
sudo apt-get install libusb-1.0-0-dev
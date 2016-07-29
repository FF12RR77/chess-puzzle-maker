# Python-Puzzle-Creator

## About

This is a python library dedicated to creating chess puzzles for lichess.org. However it can easily be adapted to create puzzles from personal games.

## Installation

This script requires the *Requests* and *Python-Chess* libraries to run, as well as a copy of *Stockfish*

### Install Requests

`pip install requests`

### Install Python Chess

`pip install python-chess`

### Setup

MacOS / Linux : `sh build-stockfish.sh` to obtain the current lichess Stockfish instance.

## Launching application

`python main.py <Secret API Token>`
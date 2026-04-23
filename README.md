\# Jarvis-Ears



Jarvis-Ears is the audio ingest service for Jarvis.



It is responsible for:

\- connecting room audio devices to Jarvis

\- receiving or adapting microphone audio streams

\- keeping short rolling audio windows in RAM

\- exposing clean interfaces for VAD and STT

\- emitting structured downstream events for Jarvis



It is not responsible for:

\- long-term memory governance

\- person identity resolution

\- final assistant UX

\- storing raw audio by default



\## Current status

This repository starts from a known-good hardware baseline:



\- M5Stack Atom Echo

\- ESPHome firmware

\- confirmed microphone config:

&#x20; - GPIO33 LRCLK

&#x20; - GPIO19 BCLK

&#x20; - GPIO23 DIN

&#x20; - PDM enabled



Open integration question:

\- how Jarvis should consume microphone audio from ESPHome directly without making Home Assistant the permanent architecture



\## Planned architecture

\- receiver layer

\- RAM ring buffer

\- VAD stage

\- STT stage

\- downstream event emission



\## Development setup

```bash

python3 -m venv .venv

source .venv/bin/activate

pip install -e .\[dev]

pytest


# Atom Echo Custom Emitter Draft

## Purpose

This document gives you a draft ESPHome experiment for the Atom Echo that sends
raw microphone callback bytes directly to the Jarvis-Ears TCP collector at
`192.168.7.210:8765`.

This is an investigation spike only. It is not production firmware and it does
not make any claim that the direct-ingest path is already verified.

## What This Draft Assumes

- The Atom Echo remains on the known microphone baseline:
  - LRCLK: `GPIO33`
  - BCLK: `GPIO19`
  - DIN: `GPIO23`
  - `pdm: true`
- The collector is already running on `192.168.7.210:8765`.
- You are flashing with the ESPHome CLI, not through Home Assistant.

## Why This Is Not YAML-Only

Current ESPHome documentation confirms that `microphone.on_data` exposes raw
audio bytes as `std::vector<uint8_t>` in automations, but YAML alone does not
provide a built-in raw TCP client action for continuously forwarding those bytes
to a custom collector. Because of that, this spike uses a local ESPHome
external component, not a YAML-only lambda.

Relevant references:

- ESPHome microphone docs:
  [https://esphome.io/components/microphone/](https://esphome.io/components/microphone/)
- ESPHome external components docs:
  [https://esphome.io/components/external_components/](https://esphome.io/components/external_components/)
- ESPHome maintainer note on removed custom components:
  [https://developers.esphome.io/blog/2025/02/19/about-the-removal-of-support-for-custom-components/](https://developers.esphome.io/blog/2025/02/19/about-the-removal-of-support-for-custom-components/)

## Files Added For The Draft

Place and keep these files exactly as they are in this repository:

- [experiments/esphome/atom_echo_tcp_emitter.yaml](C:/Development/Jarvis-Ears/experiments/esphome/atom_echo_tcp_emitter.yaml)
- [experiments/esphome/secrets.example.yaml](C:/Development/Jarvis-Ears/experiments/esphome/secrets.example.yaml)
- [experiments/esphome/components/tcp_audio_emitter/__init__.py](C:/Development/Jarvis-Ears/experiments/esphome/components/tcp_audio_emitter/__init__.py)
- [experiments/esphome/components/tcp_audio_emitter/tcp_audio_emitter.h](C:/Development/Jarvis-Ears/experiments/esphome/components/tcp_audio_emitter/tcp_audio_emitter.h)
- [experiments/esphome/components/tcp_audio_emitter/tcp_audio_emitter.cpp](C:/Development/Jarvis-Ears/experiments/esphome/components/tcp_audio_emitter/tcp_audio_emitter.cpp)

## What The Draft Emitter Does

- Configures the Atom Echo microphone using the known baseline pins and `pdm`
  mode
- Starts microphone capture automatically
- Registers a C++ callback on the microphone data path
- Queues raw callback byte chunks in RAM
- Opens a TCP connection to `192.168.7.210:8765`
- Sends each queued callback buffer as raw bytes
- Logs connect, disconnect, and send failures

## What It Does Not Do

- It does not use Home Assistant
- It does not implement VAD
- It does not implement STT
- It does not define a production framing protocol
- It does not guarantee callback boundaries are the right long-term transport
  frame boundaries
- It does not write audio to disk on the Jarvis side by default

## Manual Setup

### 1. Create `secrets.yaml`

Copy the example file and edit your Wi-Fi credentials:

```powershell
Copy-Item experiments\esphome\secrets.example.yaml experiments\esphome\secrets.yaml
```

Then edit `experiments\esphome\secrets.yaml` so it contains:

```yaml
wifi_ssid: "your-wifi-name"
wifi_password: "your-wifi-password"
```

### 2. Start The Jarvis-Ears Collector

From `C:\Development\Jarvis-Ears`:

```powershell
$env:PYTHONPATH="C:\Development\Jarvis-Ears\src;C:\Development\Jarvis-Ears"
python experiments\tcp_audio_collector.py --host 0.0.0.0 --port 8765
```

### 3. Compile The ESPHome Firmware

If `esphome` is already on your PATH:

```powershell
esphome compile experiments\esphome\atom_echo_tcp_emitter.yaml
```

### 4. Flash Over USB

Replace `COM5` with the Atom Echo serial port on your machine:

```powershell
esphome run experiments\esphome\atom_echo_tcp_emitter.yaml --device COM5
```

### 5. Watch The Logs

After boot, you should look for:

- microphone callback logs
- `Connecting to collector 192.168.7.210:8765`
- `Collector connected`
- repeated collector-side chunk logs in Jarvis-Ears

## Honesty Notes

- This draft is likely the smallest realistic path from current ESPHome
  capabilities, but it is not confirmed working yet.
- The component currently assumes the collector host is an IPv4 literal.
- The component sends raw callback bytes with no custom framing header.
- If this proves unstable, the next step is not to pretend it is production; it
  is to measure the failure mode and revise the spike.

## Exact Copy-Paste Commands

From `C:\Development\Jarvis-Ears`:

```powershell
Copy-Item experiments\esphome\secrets.example.yaml experiments\esphome\secrets.yaml
```

```powershell
$env:PYTHONPATH="C:\Development\Jarvis-Ears\src;C:\Development\Jarvis-Ears"
python experiments\tcp_audio_collector.py --host 0.0.0.0 --port 8765
```

In another terminal:

```powershell
esphome compile experiments\esphome\atom_echo_tcp_emitter.yaml
```

```powershell
esphome run experiments\esphome\atom_echo_tcp_emitter.yaml --device COM5
```

# Atom Echo Baseline

## Current Hardware

- Device: M5Stack Atom Echo
- Firmware baseline: ESPHome
- Current kitchen test device name: `atom-echo-test`
- Last known IP: `192.168.5.236`

## Known-Good Microphone Configuration

- LRCLK: GPIO33
- BCLK: GPIO19
- DIN: GPIO23
- PDM microphone: enabled

## What This Baseline Tells Us

This baseline is enough to anchor device assumptions, example configuration, and
future ingest investigation. It is not, by itself, proof of a direct
Jarvis-Ears ingest transport.

## Current Working Assumptions

- The first end-to-end work should target a single kitchen device.
- Audio should remain ephemeral and RAM-first inside Jarvis-Ears.
- Receiver integration details should stay behind an adapter boundary until the
  direct ESPHome ingest path is confirmed.

## Open Questions

- Which direct audio transport, if any, is already exposed by the current
  ESPHome baseline?
- Does the target design require a custom ESPHome component or alternate
  firmware mode?
- What framing, encoding, and delivery guarantees will Jarvis-Ears need to
  handle from the device side?

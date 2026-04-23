# ESPHome Integration Options

## Purpose

This note narrows the investigation to the smallest realistic path for
Jarvis-side microphone ingest from the current ESPHome Atom Echo baseline,
without introducing Home Assistant as a dependency in the target design.

## Current Evidence

As of April 23, 2026, current public ESPHome documentation shows two important
facts:

- The `microphone` component exposes an `on_data` trigger on-device, and that
  trigger receives raw microphone bytes as `std::vector<uint8_t>`.
- The documented `voice_assistant` component still describes the supported audio
  path as streaming microphone audio to Home Assistant for processing.

Sources:
- [ESPHome microphone component](https://esphome.io/components/microphone/)
- [ESPHome voice assistant component](https://esphome.io/components/voice_assistant/)
- [ESPHome Atom Echo issue snippet showing current known mic pins and sample rate](https://github.com/esphome/issues/issues/7123)

## What Is Known

- Device baseline: M5Stack Atom Echo
- Firmware baseline: ESPHome
- Known-good microphone wiring from current Atom Echo examples and issue reports:
  - LRCLK: GPIO33
  - BCLK: GPIO19
  - DIN: GPIO23
  - PDM microphone: enabled
  - Sample rate frequently shown as `16000`
- Jarvis-Ears already has the right high-level boundaries for:
  - receiver
  - RAM-first buffering
  - VAD handoff
  - STT handoff
  - downstream event emission
- ESPHome clearly has on-device access to raw microphone bytes.

## What Is Not Yet Confirmed

- Whether stock ESPHome exposes a supported direct off-device microphone stream
  that Jarvis-Ears can consume without Home Assistant.
- Whether the current Atom Echo baseline can emit microphone bytes over a
  transport that is stable enough for continuous ingest.
- What exact framing contract a direct stream would use:
  - sample rate
  - bits per sample
  - channel layout
  - chunk boundaries
  - reconnect behavior
  - backpressure behavior
- Whether the smallest viable direct path requires custom ESPHome code rather
  than a stock YAML-only configuration.

## Realistic Direct-Ingest Paths

### Path 1: Stock ESPHome Direct Stream Outside Home Assistant

Description:
Jarvis-Ears would connect to a documented ESPHome transport that already carries
live microphone frames directly from the device.

Why it would be best:
- Lowest long-term maintenance burden
- Keeps Jarvis-Ears in control of ingest
- Avoids extra glue layers

Current confidence:
- Low

Why confidence is low:
- The current official `voice_assistant` docs explicitly describe Home
  Assistant as the destination for streamed audio.
- The current microphone docs prove access to raw bytes on-device, but they do
  not by themselves prove a stock off-device streaming API.

What must be verified next:
- Whether any official ESPHome API, packet transport, or supported component
  can expose microphone frames directly to a non-Home-Assistant client
- Whether that path works on the Atom Echo baseline specifically

### Path 2: ESPHome Custom Component Using Microphone `on_data`

Description:
Use the documented microphone capture hooks on-device and add a minimal custom
ESPHome component that forwards framed audio to Jarvis-Ears over a narrow,
explicit transport.

Why it is realistic:
- `microphone.on_data` proves raw bytes are available on-device
- A custom component could keep the architecture Jarvis-direct
- The device-side work can be limited to one clearly scoped emitter

Tradeoffs:
- Requires custom firmware work and maintenance
- Requires defining a framing contract that Jarvis-Ears can trust
- Needs explicit handling for disconnects, capture control, and backpressure

Current confidence:
- Medium as an investigation path
- Low as a production claim until an experiment succeeds

What must be verified next:
- Whether the callback cadence and chunk sizes are stable enough for transport
- Whether the Atom Echo has enough headroom for the chosen emitter path
- Which transport is simplest and reliable enough:
  - raw TCP
  - UDP with loss tolerance
  - HTTP POST chunking
  - WebSocket

### Path 3: Temporary Home Assistant Observation Path

Description:
Use Home Assistant only to inspect what the existing voice-assistant flow proves
about microphone capture and device stability.

Why it may still help:
- Fast way to confirm the microphone path is alive on the device
- Useful for separating device-capture issues from Jarvis-side ingest issues

Tradeoffs:
- Not the target architecture
- Risks anchoring implementation thinking around the wrong permanent boundary

Allowed use:
- Temporary validation only

Not allowed use:
- Treating Home Assistant as the ongoing ingest dependency for Jarvis-Ears

## Tradeoff Summary

### Stock Direct Path

Pros:
- Cleanest architecture if it exists
- Lowest custom firmware burden

Cons:
- Not currently confirmed by official docs
- May not exist for microphone streaming outside Home Assistant

### Custom ESPHome Emitter

Pros:
- Most plausible direct path from today’s evidence
- Keeps Jarvis-direct ownership of ingest

Cons:
- Requires firmware customization
- Requires a new transport and framing contract
- Adds maintenance on both device and Jarvis sides

### Home Assistant Observation Only

Pros:
- Fast debugging aid
- Useful for proving device capture works

Cons:
- Wrong long-term boundary
- Easy to accidentally normalize as architecture

## What Would Make The Stub Replaceable

The current Jarvis-Ears receiver stub should only be replaced after all of the
following are true:

1. One direct ingest path has been demonstrated on the Atom Echo baseline.
2. Jarvis-Ears can describe the audio contract precisely.
3. Reconnect and capture-failure behavior are understood well enough to model
   in an honest receiver implementation.
4. The implementation can keep audio RAM-first without introducing default disk
   retention.

## Recommended Next Verification Questions

1. Does stock ESPHome expose any supported direct off-device microphone stream
   outside Home Assistant?
2. If not, can a minimal custom component emit microphone bytes from
   `microphone.on_data` on the Atom Echo without overrunning the device?
3. What is the smallest transport contract Jarvis-Ears could consume safely?
4. What exact success signal would justify replacing the current stub with a
   real receiver?

## Guidance For This Repo

- Keep the receiver code explicit about what is unverified.
- Avoid transport-specific production code until one path is demonstrated.
- Prefer typed placeholders that describe blockers over empty abstraction churn.
- Keep raw audio in RAM by default.

# Atom Echo Custom Emitter Spike

## Experiment Goal

Validate the smallest realistic path for direct Jarvis-side audio ingest from
the Atom Echo by using a custom ESPHome emitter that forwards microphone bytes
from `microphone.on_data` to a simple TCP collector.

This is an investigation spike only. It is not a production ingest design.

## Assumptions

- Device baseline remains M5Stack Atom Echo on ESPHome.
- The Atom Echo microphone baseline is still:
  - LRCLK: GPIO33
  - BCLK: GPIO19
  - DIN: GPIO23
  - PDM microphone enabled
- The device can access raw microphone bytes via ESPHome `microphone.on_data`.
- Home Assistant is not part of the target path.
- The collector should keep received audio in memory unless debug artifact
  writing is explicitly enabled.

## Expected Data Flow

1. Atom Echo captures microphone data through the existing ESPHome microphone
   configuration.
2. `microphone.on_data` hands raw bytes to a narrow custom emitter component on
   the device.
3. The custom emitter opens a TCP connection to a Jarvis-side experimental
   collector.
4. The collector records:
   - connection timing
   - chunk sizes
   - total bytes
   - chunk cadence
5. The collector does not act as production ingest. Its purpose is only to
   produce evidence about the wire shape and device behavior.

## Draft ESPHome-Side Emitter Note

The intended custom emitter approach is:

- Keep the Atom Echo microphone config as close to the known baseline as
  possible.
- Attach custom code at the point where `microphone.on_data` exposes raw bytes.
- Send those bytes off-device with the least extra framing possible for the
  first experiment.

Initial emission shape to try:

- one TCP connection from Atom Echo to the collector
- each callback forwards one byte chunk as received
- no compression
- no attempt at VAD or STT on-device
- no disk writes on the Jarvis side by default

What the Atom should send to the collector:

- raw audio bytes from each callback
- enough implied or explicit metadata to interpret the session:
  - device name
  - sample rate
  - channels
  - bits per sample

What still needs to be measured:

- callback chunk size distribution
- callback cadence
- whether callback boundaries are stable enough to treat as transport frames
- whether the Atom stays stable while emitting continuously
- disconnect and reconnect behavior

This emitter approach is not confirmed working yet. It is only the narrowest
custom path suggested by the current evidence.

## Risks

- `microphone.on_data` may fire too often or with chunk sizes too small for a
  naive TCP emitter.
- The Atom Echo may not have enough headroom for sustained microphone capture
  plus network emission.
- Callback timing may jitter enough that a production framing contract will need
  additional structure.
- Disconnect handling may be messy enough to require explicit session framing.
- Writing debug artifacts could accidentally normalize raw-audio disk retention
  if it is not kept clearly opt-in.

## Evidence To Capture

- exact ESPHome version used
- exact Atom Echo YAML or external component code used
- collector host and port used
- observed chunk sizes
- total bytes received over time
- average inter-chunk delta
- whether the first chunk arrives promptly after capture starts
- what happens on emitter reconnect or device reboot
- whether the device remains stable during a short continuous run

## Definition Of Success

The spike is successful if all of the following are true:

1. The Atom Echo connects directly to the experimental collector without Home
   Assistant in the path.
2. The collector receives repeated raw byte chunks in memory.
3. Chunk size and cadence are observable enough to describe a candidate framing
   contract.
4. The device remains stable long enough to complete a short controlled test.
5. The results are clear enough to state whether a real `AudioReceiver` is now
   justified or whether more firmware-side investigation is still required.

## Sample Collector Commands

Run the collector without writing any audio artifact:

```powershell
$env:PYTHONPATH="C:\Development\Jarvis-Ears\src;C:\Development\Jarvis-Ears"
python experiments\tcp_audio_collector.py --host 0.0.0.0 --port 8765
```

Run the collector with explicit debug artifact writing enabled:

```powershell
$env:PYTHONPATH="C:\Development\Jarvis-Ears\src;C:\Development\Jarvis-Ears"
python experiments\tcp_audio_collector.py `
  --host 0.0.0.0 `
  --port 8765 `
  --write-debug-artifact `
  --debug-output experiments\captures\atom-echo-test.bin
```

Use debug artifact writing only when you intentionally want a temporary capture
for inspection.

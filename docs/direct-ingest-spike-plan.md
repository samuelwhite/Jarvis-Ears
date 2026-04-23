# Direct Ingest Spike Plan

## Goal

Find the smallest realistic path to replace the current ESPHome receiver stub
with a real Jarvis-side ingest receiver for the Atom Echo baseline, without
introducing Home Assistant as a dependency in the target architecture.

## Scope

This is an investigation spike, not a production transport implementation.

The spike should answer:

- whether a direct ingest path exists today with stock ESPHome
- whether a minimal custom ESPHome emitter is required
- what exact evidence is needed before Jarvis-Ears should implement a real
  receiver

## Concrete Investigation Steps

1. Inspect current official ESPHome documentation and source references for any
   supported off-device microphone streaming path outside Home Assistant.
2. Confirm the current Atom Echo microphone baseline in a minimal ESPHome config:
   pins, PDM mode, sample rate, and capture behavior.
3. Determine whether `microphone.on_data` can be used as the narrow hook for a
   custom emitter.
4. Choose one candidate direct transport for experiment only.
5. Capture evidence about chunk size, cadence, disconnect handling, and device
   stability.
6. Decide whether the result is strong enough to replace the stub or whether the
   repo should stay in stub mode while the firmware path is investigated further.

## Suggested Experiments

### Experiment A: Stock Capability Check

Question:
Does stock ESPHome already provide a supported direct stream to a non-Home
Assistant client?

Success evidence:
- Official docs or source show a supported direct path
- A test device can emit microphone audio to a non-Home-Assistant endpoint

Failure evidence:
- No supported direct path can be found
- All documented streaming paths terminate in Home Assistant

### Experiment B: Minimal Custom Emitter Proof

Question:
Can the Atom Echo emit raw microphone frames from `microphone.on_data` through a
minimal custom component without collapsing stability?

Success evidence:
- Device emits repeated microphone frames to a simple Jarvis-side collector
- Captured metadata shows stable sample format and chunk cadence
- Basic disconnect and restart behavior can be observed

Failure evidence:
- The callback is too unstable or too expensive on-device
- Device crashes, drops capture quickly, or cannot sustain emission

### Experiment C: Jarvis-Side Framing Trial

Question:
Can Jarvis-Ears accept one verified stream shape and convert it into `AudioChunk`
objects while keeping all audio RAM-first?

Success evidence:
- A collector receives bytes in memory only
- The collector can attach honest metadata:
  - device name
  - sample rate
  - channels
  - sample width
  - receive timestamp

Failure evidence:
- The wire format is too ambiguous
- The receiver cannot determine chunk boundaries reliably

## Expected Evidence To Record

- Exact ESPHome version used for the experiment
- Exact Atom Echo config used for the experiment
- Whether the path is stock or custom
- Sample rate, bits per sample, and channel count actually observed
- Chunk sizes and chunk cadence
- Behavior under reconnect or capture restart
- Device stability notes:
  - CPU pressure
  - memory pressure
  - dropped frames
  - reboot/crash behavior

## Minimum Viable Success Definition

The receiver stub is ready to be replaced only if the spike produces all of the
following:

1. One direct ingest path works on the Atom Echo baseline without depending on
   Home Assistant as the ingest service.
2. The audio format is explicit and repeatable.
3. Jarvis-Ears can model incoming frames as `AudioChunk` objects honestly.
4. The receiver can remain RAM-first with no default raw-audio disk retention.
5. Failure modes are known well enough to implement `start`, `stop`, and
   reconnect behavior without pretending unknowns are solved.

## Non-Success But Still Valuable Outcomes

- Proof that stock ESPHome does not currently expose the needed direct path
- Proof that a custom emitter is required
- Proof that one candidate transport is a dead end

Those outcomes still reduce risk and should be documented before any larger
implementation work begins.

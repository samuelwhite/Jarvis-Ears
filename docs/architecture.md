# Jarvis-Ears Architecture

## Purpose

Jarvis-Ears is the room-audio ingest service for Jarvis. Its near-term job is to
accept audio from room devices, keep only recent audio in RAM, hand audio
through clean VAD and STT boundaries, and emit structured downstream events.

## Boundaries

### Jarvis-Ears

Jarvis-Ears owns:

- device-facing ingest adapters
- short-lived RAM buffering for recent audio
- VAD integration points
- STT integration points
- downstream event production for Jarvis

Jarvis-Ears does not own:

- long-term memory governance
- person identity resolution
- final assistant UX
- silent raw-audio persistence to disk

### Jarvis

Jarvis should treat Jarvis-Ears as a dedicated ingest pipeline component. Jarvis
can consume events such as speech detection and transcripts, but Jarvis-Ears
should not absorb broader orchestration concerns that belong to Jarvis.

### Alfred

Alfred is downstream of this repository's core responsibility. If Alfred
consumes speech- or transcript-derived events, that handoff should happen via
explicit event contracts rather than by merging Alfred logic into Jarvis-Ears.

### People-Service

Identity attribution is explicitly out of scope for this repository. Any speaker
identity, room-presence attribution, or person linkage belongs in people-service
and should remain separate from the ingest and transcription path.

## Intended Pipeline Shape

The current target shape is:

1. Device ingest receives live audio chunks.
2. RAM ring buffer retains only the most recent audio window.
3. VAD decides whether audio likely contains speech.
4. STT turns selected audio into text.
5. Jarvis-Ears emits structured downstream events.

The current codebase implements the package structure, config models, RAM ring
buffer, and interface boundaries. Direct ESPHome ingest, real VAD, and real STT
remain intentionally stubbed until their integration details are verified.

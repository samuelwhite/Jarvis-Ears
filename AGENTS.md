\# AGENTS.md



\## Repository purpose

This repository is for Jarvis audio ingest from room devices, starting with M5Stack Atom Echo units running ESPHome.



Current goal:

\- Build the Jarvis-side ingest path.

\- Keep audio ephemeral and RAM-first.

\- Separate ingest, buffering, VAD, STT, and memory-candidate handoff cleanly.



Non-goals for now:

\- Do not build full assistant UX here.

\- Do not hard-wire Home Assistant as the permanent architecture.

\- Do not fake working ESPHome audio ingest if a step is still uncertain.



\## Working rules

\- Keep changes small and well-scoped.

\- Prefer clear interfaces and stubs over speculative implementations.

\- Preserve a clean separation between:

&#x20; - device ingest

&#x20; - RAM buffering

&#x20; - VAD

&#x20; - STT

&#x20; - downstream event emission

\- Do not store raw audio on disk by default.

\- If a temporary audio artifact is needed for debugging, make it explicit, optional, and easy to remove.

\- Treat identity attribution as out of scope for this repo; that belongs to people-service.



\## Current known hardware baseline

\- Device: M5Stack Atom Echo

\- Firmware baseline: ESPHome

\- Known-good mic config:

&#x20; - GPIO33 LRCLK

&#x20; - GPIO19 BCLK

&#x20; - GPIO23 DIN

&#x20; - PDM microphone enabled

\- Current kitchen test device:

&#x20; - name: atom-echo-test

&#x20; - IP: 192.168.5.236



\## Engineering expectations

\- Use Python.

\- Prefer simple, typed code.

\- Add tests for non-hardware logic.

\- Keep external integration points behind interfaces.

\- Document assumptions and open questions in `docs/`.



\## Validation before finishing work

\- Run tests if you changed tested code.

\- Update docs if you changed architecture, config, or workflow.

\- Be explicit about what is implemented vs stubbed.



\## Review guidelines

\- Do not introduce silent disk retention of raw audio.

\- Do not mix room-audio ingest concerns with memory governance concerns.

\- Do not hard-code secrets, tokens, or passwords.

\- Flag uncertain ESPHome audio-consumption details clearly in code and docs.


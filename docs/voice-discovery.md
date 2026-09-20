# Voice and natural-language discovery

Implemented in the computer prototype on 20 September 2026. This is not ESP32 firmware or a validated microphone hardware design.

Find music → **Ask for music** accepts requests such as “chilled electronic bass, like Bonobo but a little more upbeat.” OpenAI returns a listening brief and three suggested artists with reasons. Refine that brief with requests such as “more danceable, fewer vocals.” **Explore** searches the live TIDAL catalogue; selecting a returned artist opens native Naim browsing. Suggestions are not claimed to be verified TIDAL results until searched.

**Speak** records a short microphone clip, with Stop, Cancel and a 30-second cutoff. Review the transcript before submitting a search. Voice input also works in ordinary catalogue search. Leaving the page, hiding the tab or cancelling stops capture. There is no wake word, background listening or automatic playback.

## Services and privacy

- Music interpretation uses the OpenAI Responses API with gpt-4.1-mini and structured output. The model can be changed with --ai-model.
- Transcription uses gpt-4o-mini-transcribe. WebM, MP4 and WAV uploads are bounded to 3 MiB and retained only in process memory by the app.
- Requests, previous brief context and submitted voice clips go to OpenAI. The app does not log bodies or save recordings. Responses requests use store=false; this is not a claim of zero provider retention.
- Keys stay in the local Python process, never browser JavaScript. The key was created through secure Platform setup and saved only to the user-approved ignored destination.
- AI output supplies search terms, never device commands or invented catalogue IDs. Native Naim resolution remains required before Play. The NDX 2 retrieves and decodes music itself.

Sources: [structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs), [transcription](https://developers.openai.com/api/docs/guides/speech-to-text), [GPT-4.1 mini](https://developers.openai.com/api/docs/models/gpt-4.1-mini).

## Running

```sh
python tools/prototype_ui.py --ai --openai-env-file PATH_TO_APPROVED_ENV_FILE --tidal --ndx NDX_IP
```

The explicit file reader reads only OPENAI_API_KEY and does not execute env-file content. Without a file argument, --ai reads the key from the process environment. TIDAL uses the existing hidden prompts or environment variables. Never pass secret values as arguments. No key is created or rotated at application startup.

Omit --ndx to simulate playback. Omit --tidal to leave catalogue lookup unconfigured: AI suggestions still work, but Explore states that no result has been verified. Omit --ai for the original prototype.

## Evidence and remaining work

Live AI requests and refinements passed. In the browser, the Bonobo-style request produced Tycho as a suggestion; Explore returned live TIDAL artists and selecting Tycho opened its native Naim albums. Separately through the same UI, public search → Teardrop → native playback passed with advancing position, TIDAL source/queue identity and error=0. Cleanup left the player stopped.

34 offline tests pass, covering structured responses, context, bounds, safe errors, native validation and HTTP origin checks. The user tested Speak with the Bonobo request and confirmed that the transcript appeared correctly. This verifies capture and live transcription in that browser session; it does not validate future ESP32 microphone hardware. Unsupported microphone APIs or denied permission produce a message and leave typing available.

The final build needs microphone selection, an acoustic opening, capture tests near playing music, and power/wake measurements. Do not assume the selected Waveshare already has a suitable microphone. AI processing is off the handheld; a Pi bridge remains a deployment candidate. UI theme variables keep colours adjustable to the final enclosure material.

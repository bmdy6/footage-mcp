# Audio API recordings

Tests only read these files and mock HTTP; no credentials or network needed.

Recorded 2026-11-12 from anonymous API responses:
- `openverse.json`: `https://api.openverse.org/v1/audio/?q=upbeat%20ukulele&page_size=5` (duration is milliseconds).
- `commons.json`: Commons Action API search `piano filetype:audio`, namespace 6, imageinfo URL/extmetadata/size/MIME, limit 2.
- `archive.json`: Archive advanced search `ukulele AND mediatype:audio AND (licenseurl:*publicdomain* OR licenseurl:*creativecommons*)`, 2 results.
- `nasa.json`: `https://images-api.nasa.gov/search?q=apollo&media_type=audio&page_size=2`; long transcript descriptions truncated to 250 characters.
- `edge-voices.json`: edge-tts 7.3.1 `list_voices()` response filtered to `Locale == zh-CN`.

No Freesound/Jamendo keys were available, so their fixtures reuse publicly saved API responses, **not** a live check of these integrations:
- `freesound.json`: first sound from [tide-app/tide sound.json](https://github.com/tide-app/tide/blob/fe7a893ef260faa6edfa40aace08da90c98e667b/cypress/fixtures/sound.json), wrapped in `results` for the search parser. Original license and HQ preview URL retained. Tests separately exercise named-license variants and missing previews.
- `jamendo.json`: first two results from [Connorcorc/musicLink sampleData.json](https://github.com/Connorcorc/musicLink/blob/e67be9d9c4085c4cc99a2cad781de3e75c1385b9/cypress/fixtures/sampleData.json). Removed pagination URL containing a public client ID, signed `from` query parameter, and large waveform strings. Includes the upstream download-permission field. Test variants separately cover denied/missing permissions and a CC BY URL; commercial clearance stays false.

Fixtures are metadata, not audio files. License values are evidence for parser tests, not permission to reuse the recordings in a product.

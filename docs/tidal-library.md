# TIDAL collection and navigation

The heart is TIDAL's My Collection action: like a track, save an album or playlist, or save an artist. Saving an album does not automatically like all its tracks. These are account changes, separate from adding something to the play queue.

## Prototype flow

1. Open Collection → Connect TIDAL library. Sign in with the same account used in the Naim app.
2. Open an album, track, artist or playlist from search or Collection. The detail page checks its saved state and offers a heart action.
3. Use Collection's Albums, Liked tracks, Artists and Playlists filters to browse saved music. More saved music follows the service's cursor.
4. Now Playing → Track details / save resolves the current queue item's actual TIDAL ID. It does not infer an ID from the song title.
5. Back stays in the top bar, including AI discovery and collection folders. It restores the previous query, filter, results, pagination and scroll position. Leaving a voice-input screen cancels recording.

The existing Play now, Play next and Add to queue controls remain native Naim commands. This collection integration cannot relay or play audio.

## Developer configuration

In this project's TIDAL developer app, register `http://127.0.0.1:8990/oauth/callback` and allow only `collection.read` and `collection.write`. For another server port, register that exact loopback callback before connecting. No playback or email/profile permission is requested.

Run the usual prototype with `--tidal`, optionally `--ndx NDX_IP` and the existing AI configuration. OAuth uses an unpredictable single-use state and PKCE S256. Authorization expires after ten minutes if unfinished. Access and refresh tokens live only in the Python process; restarting it requires Connect again. Disconnect clears local authorization, not the user's TIDAL subscription or collection. Revocation in the TIDAL account is separate. Persistent credential storage remains deployment work.

The adapter uses the official v2 `userCollectionAlbums`, `userCollectionTracks`, `userCollectionArtists` and `userCollectionPlaylists` relationship endpoints with `me`. Saved-state checks follow all pages, cache a complete snapshot for up to 60 seconds, and never interpret an incomplete read as “not saved.” Save/remove reads fresh state first, sends at most one write, and reads back the result. Rate-limited reads may wait and retry once; writes are not automatically retried. The bounded scan rejects collections exceeding 100 pages instead of inventing a heart state.

TIDAL clients may take time to show changes made by another client. The controller's verification is an account API read-back; Naim-app synchronization is a separate observation. Choose the same TIDAL account manually: the native player's login identity is not exposed or compared by this prototype.

## Coverage and remaining work

Implemented: collection read/save/remove for the four types, account sign-in/disconnect, native current-track details and persistent Back navigation. Pure demo hearts are explicitly simulated and reset with the page.

Still planned: playlist creation and editing, queue editing in the UI, shuffle/repeat/seek UI, related album/artist shortcuts, favourites directly on result rows, persistent sign-in for deployment, and physical touchscreen testing. Do not describe this prototype as complete TIDAL feature parity.

Offline checks: `python -m unittest discover -s tests -v` and `node tests/test_navigation.cjs`. Save/remove round trips for all four types passed live with original test states restored. Live account evidence is recorded separately in [the evidence ledger](evidence.md).

Sources: [official TIDAL API reference](https://tidal-music.github.io/tidal-api-reference/), [machine-readable specification](https://tidal-music.github.io/tidal-api-reference/tidal-api-oas.json), and [TIDAL's favourite-content guide](https://support.tidal.com/hc/en-us/articles/115005843325-Web-Player-How-to-Favorite-and-Delete-Content). Inspected 20 September 2026.

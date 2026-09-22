#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "bridge_protocol.h"

typedef enum { NOW, FIND, DETAILS, COLLECTION, QUEUE, VOICE, SETTINGS, DISPLAY, CONNECTION, DEVICE, WIFI, PAIRING } screen_t;
typedef enum { SAVED_UNKNOWN, SAVED_NO, SAVED_YES } saved_t;
typedef enum { VOICE_IDLE, VOICE_RECORDING, VOICE_STOPPED } voice_t;
typedef enum { OUTCOME_NONE, OUTCOME_PENDING, OUTCOME_SUBMITTED, OUTCOME_UNKNOWN } outcome_t;
typedef struct {
    screen_t screen;
    char query[257];
    char filter[16];
    char cursor[4097];
    unsigned offset;
    int scroll;
    bridge_item_t items[BRIDGE_PAGE_MAX];
    unsigned count;
    int next_offset;
    char result_id[257];
    bridge_item_t selected;
    bool playable;
    saved_t saved;
} context_t;
typedef struct {
    context_t context, history[4];
    unsigned depth;
    bool online, consume_contact, busy;
    uint64_t fresh_until, recording_until;
    voice_t voice;
    outcome_t outcome;
    char title[257], transcript[257];
    bridge_item_t current;
    char artist[257], album[257], source[257], transport[32], account[32];
    int position_ms, duration_ms, bitrate;
    saved_t track_saved;
    unsigned palette, brightness, timeout;
    bool fixture;
    uint32_t generation;
    char error_code[49];
} controller_t;

/* Hardware and transport belong behind these interfaces. No revision pins here. */
typedef struct {
    uint64_t (*now_ms)(void);
    void (*diagnostic)(const char *event);
    bool (*snapshot)(controller_t *state); /* authoritative; no mutations */
    bool (*native_play_once)(const char *candidate); /* bridge resolves native */
    bool (*amplifier_once)(bool up); /* bridge owns exact D011 sequence */
    bool (*backlight)(bool on);
    bool (*sleep)(unsigned mode); /* must fail until revision wake audit passes */
    int (*battery_percent)(void); /* -1 means unknown */
    bool (*microphone_start)(void);
    void (*microphone_cancel)(void);
    /* Optional authenticated network backend. UI thread alone owns state. */
    bool (*submit)(const bridge_request_t *request);
    bool (*poll)(bridge_reply_t *reply);
    void (*invalidate)(uint32_t generation);
    void (*request_id)(char out[49]);
} platform_t;

void controller_init(controller_t *s);
void controller_disconnect(controller_t *s);
void controller_snapshot(controller_t *s, uint64_t now);
bool controller_touch(controller_t *s, bool pressed);
bool controller_available(const controller_t *s, uint64_t now);
void controller_push(controller_t *s, screen_t screen);
void controller_back(controller_t *s);
bool controller_voice_start(controller_t *s, uint64_t now);
bool controller_voice_tick(controller_t *s, uint64_t now);
void controller_voice_cancel(controller_t *s);

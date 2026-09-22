#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#define BRIDGE_REQUEST_MAX 8192
#define BRIDGE_RESPONSE_MAX 32768
#define BRIDGE_PAGE_MAX 12
typedef enum { BR_SNAPSHOT, BR_SEARCH, BR_BROWSE, BR_PLAY, BR_AMP_UP, BR_AMP_DOWN,
               BR_QUEUE, BR_SAVED, BR_SAVE, BR_REMOVE, BR_TRANSPORT, BR_LIBRARY, BR_VOICE } bridge_action_t;
typedef struct {
    char reference[257], title[257], artist[257], album[257], kind[16];
    char artist_reference[257], album_reference[257];
    int saved; /* -1 unknown, 0 unsaved, 1 saved */
} bridge_item_t;
typedef struct {
    bridge_action_t action;
    uint32_t generation;
    uint64_t started_ms;
    char kind[16];
    char id[49], text[257], cursor[4097], result_id[257];
    unsigned offset;
} bridge_request_t;
typedef struct {
    bridge_action_t action;
    uint32_t generation;
    uint64_t started_ms;
    bool valid, fixture, playable;
    enum { BR_OBSERVED, BR_SUBMITTED, BR_REJECTED, BR_UNKNOWN } outcome;
    unsigned valid_for_ms, count;
    int next_offset, saved;
    char title[257], boot_id[65], cursor[4097], result_id[257];
    char error_code[49];
    bridge_item_t item, items[BRIDGE_PAGE_MAX];
    char artist[257], album[257], source[257], transport[32], account[32], transcript[257];
    int position_ms, duration_ms, bitrate;
} bridge_reply_t;
bool bridge_mutation(bridge_action_t action);
bool bridge_encode(const bridge_request_t *request, char *json, size_t capacity);
bool bridge_decode(const bridge_request_t *request, const char *json, size_t size, bridge_reply_t *reply);

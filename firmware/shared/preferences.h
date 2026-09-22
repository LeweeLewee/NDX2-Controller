#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#define PREFERENCES_BYTES 12
/* Non-secret, local display intent only; never commands or credentials. */
typedef struct { unsigned palette, brightness, timeout; } preferences_t;
typedef enum { PREF_DEFAULTS, PREF_LOADED, PREF_UNAVAILABLE } preferences_result_t;
void preferences_defaults(preferences_t *p);
bool preferences_valid(const preferences_t *p);
bool preferences_encode(const preferences_t *p,uint8_t out[PREFERENCES_BYTES]);
bool preferences_decode(const uint8_t *data,size_t size,preferences_t *p);

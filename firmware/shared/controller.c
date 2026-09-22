#include "controller.h"
#include <string.h>

void controller_init(controller_t *s) {
    memset(s, 0, sizeof(*s));
    s->consume_contact = true;
    s->fixture = true;
    s->context.next_offset = -1;
    s->brightness=80; s->timeout=2;
    s->position_ms=s->duration_ms=s->bitrate=-1;
    strcpy(s->context.filter, "albums");
    strcpy(s->title, "SILENT FIXTURE - reconnecting");
}
bool controller_voice_start(controller_t *s, uint64_t now) {
    controller_voice_cancel(s);
    if(!s->fixture||!controller_available(s,now)) return false;
    s->voice=VOICE_RECORDING; s->recording_until=now+30000; return true;
}
bool controller_voice_tick(controller_t *s, uint64_t now) {
    if(s->voice!=VOICE_RECORDING||now<s->recording_until) return false;
    s->voice=VOICE_STOPPED; return true; /* explicit submission only */
}
void controller_voice_cancel(controller_t *s) {
    s->voice = VOICE_IDLE;
    s->recording_until=0;
    memset(s->transcript, 0, sizeof(s->transcript));
}
void controller_disconnect(controller_t *s) {
    s->generation++;
    s->online = false; s->fresh_until = 0; s->consume_contact = true;
    if (s->busy) s->outcome = OUTCOME_UNKNOWN;
    s->busy = false;
    controller_voice_cancel(s);
}
void controller_snapshot(controller_t *s, uint64_t now) {
    s->online = true; s->fresh_until = now + 5000;
}
bool controller_touch(controller_t *s, bool pressed) {
    if (s->consume_contact) {
        if (!pressed) s->consume_contact = false;
        return false;
    }
    return pressed;
}
bool controller_available(const controller_t *s, uint64_t now) {
    return s->online && now < s->fresh_until && !s->consume_contact && !s->busy;
}
void controller_push(controller_t *s, screen_t screen) {
    if (s->depth == 4) {
        memmove(s->history, s->history + 1, 3 * sizeof(context_t)); s->depth = 3;
    }
    s->history[s->depth++] = s->context;
    s->context.screen = screen; s->context.scroll=0; controller_voice_cancel(s);
}
void controller_back(controller_t *s) {
    if (s->depth) s->context = s->history[--s->depth];
    controller_voice_cancel(s);
}

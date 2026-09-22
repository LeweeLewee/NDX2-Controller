#include <assert.h>
#include <string.h>
#include "fixture.h"
static unsigned commands;
static uint64_t now(void) { return 100; }
static void log_event(const char *s) { if(!strcmp(s,"fixture_transport_once")) commands++; }
static bridge_reply_t exchange(platform_t *p,bridge_action_t action,const char *text) {
    bridge_request_t r={0}; bridge_reply_t reply; r.action=action; r.started_ms=100;
    if(text) strcpy(r.text,text);
    assert(p->submit(&r)); assert(p->poll(&reply)); assert(reply.valid); return reply;
}
int main(void) {
    platform_t p=fixture_platform(now,log_event);
    bridge_reply_t r=exchange(&p,BR_SNAPSHOT,NULL); assert(!strcmp(r.transport,"playing"));
    exchange(&p,BR_TRANSPORT,"pause"); r=exchange(&p,BR_SNAPSHOT,NULL); assert(!strcmp(r.transport,"paused"));
    exchange(&p,BR_TRANSPORT,"resume"); r=exchange(&p,BR_SNAPSHOT,NULL); assert(!strcmp(r.transport,"playing")&&commands==2);
    exchange(&p,BR_TRANSPORT,"pause"); exchange(&p,BR_PLAY,"inputs/tidal/tracks/101");
    r=exchange(&p,BR_SNAPSHOT,NULL); assert(!strcmp(r.transport,"playing"));
    return 0;
}

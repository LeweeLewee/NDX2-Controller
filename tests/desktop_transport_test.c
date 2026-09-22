/* Real desktop worker/helper against tools/m2_recovery_demo.py TLS fixtures. */
#define SDL_MAIN_HANDLED
#include <SDL.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "transport.h"
static platform_t platform;
static bridge_reply_t reply;
static void phase(const char *name) {
    char ack[16]; puts(name); fflush(stdout); assert(fgets(ack,sizeof(ack),stdin));
}
static void exchange(bridge_action_t action) {
    bridge_request_t r={0}; r.action=action; r.started_ms=SDL_GetTicks64();
    strcpy(r.text,"inputs/tidal/albums/1"); platform.request_id(r.id);
    assert(platform.submit(&r)); uint64_t deadline=SDL_GetTicks64()+10000;
    while(!platform.poll(&reply)) { assert(SDL_GetTicks64()<deadline); SDL_Delay(5); }
}
int main(int argc,char **argv) {
    assert(argc==3); SDL_SetMainReady(); assert(SDL_Init(SDL_INIT_TIMER)==0);
    assert(desktop_transport_init(&platform,argv[1],argv[2]));
    exchange(BR_SNAPSHOT); assert(!reply.valid); phase("START");
    exchange(BR_SNAPSHOT); assert(reply.valid&&reply.outcome==BR_OBSERVED);
    char first_boot[65]; strcpy(first_boot,reply.boot_id);
    phase("DELAY_READ"); exchange(BR_SNAPSHOT); assert(!reply.valid);
    exchange(BR_SNAPSHOT); assert(reply.valid&&reply.outcome==BR_OBSERVED);
    phase("DELAY_PLAY"); uint64_t start=SDL_GetTicks64(); exchange(BR_PLAY);
    assert(!reply.valid&&reply.outcome==BR_UNKNOWN&&SDL_GetTicks64()-start>=6400);
    exchange(BR_SNAPSHOT); assert(reply.valid&&reply.outcome==BR_OBSERVED);
    phase("DELAY_AMPLIFIER"); exchange(BR_AMP_UP); assert(!reply.valid&&reply.outcome==BR_UNKNOWN);
    exchange(BR_SNAPSHOT); assert(reply.valid&&reply.outcome==BR_OBSERVED);
    phase("RESTART"); exchange(BR_SNAPSHOT);
    assert(reply.valid&&strcmp(first_boot,reply.boot_id));
    desktop_transport_close(); SDL_Quit();
    puts("PASS desktop startup outage, delayed read, lost mutation responses and bridge restart");
    return 0;
}

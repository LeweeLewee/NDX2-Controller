/* Deterministic native LVGL event/reply tests, no network or audio. */
#include <assert.h>
#include <string.h>
#include <stdio.h>
/* Include the renderer to inspect its private single-flight state in this test. */
#include "../firmware/shared/ui.c"
static uint64_t clock_ms=100;
static bridge_request_t sent;
static bool occupied, deliver;
static bridge_reply_t incoming;
static unsigned submissions;
static uint64_t clock_now(void) { return clock_ms; }
static void diagnostic(const char *s) { (void)s; }
static void cancel(void) {}
static bool start(void) { return true; }
static bool submit_test(const bridge_request_t *r) {
    if(occupied) return false;
    sent=*r; occupied=true; submissions++; return true;
}
static bool poll_test(bridge_reply_t *r) {
    if(!deliver) return false;
    *r=incoming; occupied=deliver=false; return true;
}
static void invalidated(uint32_t g) { (void)g; }
static void identity(char out[49]) { strcpy(out,"0123456789abcdef0123456789abcdef"); }
static void flush_test(lv_disp_drv_t *d,const lv_area_t *a,lv_color_t *c) { (void)a; (void)c; lv_disp_flush_ready(d); }
static lv_obj_t *find_action(lv_obj_t *o,unsigned action) {
    if((uintptr_t)lv_obj_get_event_user_data(o,click)==action) return o;
    for(unsigned i=0;i<lv_obj_get_child_cnt(o);i++) { lv_obj_t *found=find_action(lv_obj_get_child(o,i),action); if(found) return found; }
    return NULL;
}
static void tap_action(unsigned action) {
    lv_obj_t *o=find_action(root,action); assert(o&&!lv_obj_has_state(o,LV_STATE_DISABLED));
    lv_event_send(o,LV_EVENT_PRESSED,NULL); lv_event_send(o,LV_EVENT_RELEASED,NULL); lv_event_send(o,LV_EVENT_CLICKED,NULL);
    tick(NULL);
}
int main(void) {
    lv_init(); static lv_color_t buffer[800]; static lv_disp_draw_buf_t draw;
    lv_disp_draw_buf_init(&draw,buffer,NULL,800);
    static lv_disp_drv_t display; lv_disp_drv_init(&display); display.hor_res=800; display.ver_res=480;
    display.draw_buf=&draw; display.flush_cb=flush_test; lv_disp_drv_register(&display);
    platform_t platform={.now_ms=clock_now,.diagnostic=diagnostic,.microphone_cancel=cancel,.microphone_start=start,
        .submit=submit_test,.poll=poll_test,.invalidate=invalidated,.request_id=identity};
    controller_ui_init(&platform);
    controller_snapshot(&state,clock_ms); controller_ui_touch(false); next_read=2000;
    controller_push(&state,VOICE); start_capture(); render();
    tap_action(18); assert(sent.action==BR_VOICE&&network_pending);
    uint32_t old_generation=sent.generation;
    tap_action(17); assert(state.generation!=old_generation&&state.voice==VOICE_RECORDING);
    incoming=(bridge_reply_t){.valid=true,.action=BR_VOICE,.generation=old_generation,.outcome=BR_OBSERVED};
    strcpy(incoming.transcript,"Discarded recording"); deliver=true; tick(NULL);
    assert(state.context.screen==VOICE&&state.voice==VOICE_RECORDING&&submissions==1&&!state.context.query[0]);
    tap_action(18); tap_action(19);
    incoming.generation=sent.generation; deliver=true; tick(NULL);
    assert(state.context.screen==NOW&&state.voice==VOICE_IDLE&&submissions==2&&!state.context.query[0]);
    puts("PASS native transcription restart/cancel reject late replies");
    strcpy(state.current.artwork,"/artwork/a.jpg"); tick(NULL);
    assert(sent.action==BR_ARTWORK);
    incoming=(bridge_reply_t){.valid=true,.action=BR_ARTWORK,.generation=sent.generation,
        .started_ms=clock_ms,.outcome=BR_OBSERVED,.artwork_available=true,.valid_for_ms=60000};
    strcpy(incoming.artwork,sent.text); incoming.pixels[0]=0xf800; deliver=true; tick(NULL);
    assert(artwork_loaded&&artwork_widget);
    state.current.artwork[0]=0; tick(NULL); assert(!artwork_loaded);
    strcpy(state.current.artwork,"/artwork/a.jpg"); tick(NULL);
    strcpy(state.current.artwork,"/artwork/b.jpg"); deliver=true; tick(NULL);
    assert(!artwork_loaded&&!strcmp(sent.text,"/artwork/b.jpg"));
    incoming.valid=false; deliver=true; tick(NULL);
    assert(!artwork_loaded&&state.online&&!network_pending);
    unsigned count=submissions; tick(NULL); assert(submissions==count); /* no retry loop */
    clear_artwork(); tick(NULL); /* explicit new attempt */
    incoming.valid=true; strcpy(incoming.artwork,sent.text); deliver=true; tick(NULL);
    assert(artwork_loaded);
    clock_ms=state.fresh_until; sync_artwork(); assert(!artwork_loaded); /* stale state hides cover */
    controller_snapshot(&state,clock_ms); next_read=clock_ms+2000; tick(NULL);
    uint32_t image_generation=sent.generation;
    controller_ui_disconnect(); incoming.generation=image_generation; deliver=true; tick(NULL);
    assert(!artwork_loaded&&!state.online); /* obsolete image cannot revive a disconnect */
    puts("PASS native artwork identity/missing/corrupt/stale/disconnect and bounded retry");
    return 0;
}

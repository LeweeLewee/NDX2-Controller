#include "controller.h"
#include <assert.h>
#include <string.h>
int main(void) {
    controller_t s; controller_init(&s); controller_snapshot(&s,100);
    assert(!controller_touch(&s,true)); assert(!controller_touch(&s,false));
    assert(controller_available(&s,101)); assert(!controller_available(&s,5100));
    strcpy(s.context.query,"quiet"); s.context.scroll=220; s.context.offset=12;
    controller_push(&s,DETAILS); controller_back(&s);
    assert(s.context.scroll==220 && s.context.offset==12 && !strcmp(s.context.query,"quiet"));
    s.busy=true; s.voice=VOICE_RECORDING; controller_disconnect(&s);
    assert(s.outcome==OUTCOME_UNKNOWN && !s.busy && s.voice==VOICE_IDLE);
    assert(s.context.scroll==220 && !controller_available(&s,102));
    controller_touch(&s,false); controller_snapshot(&s,1000);
    strcpy(s.context.filter,"artists"); strcpy(s.context.cursor,"opaque_cursor");
    strcpy(s.context.selected.reference,"inputs/tidal/artists/1"); s.context.saved=SAVED_YES;
    controller_push(&s,DETAILS); strcpy(s.context.selected.reference,"inputs/tidal/albums/2");
    s.context.saved=SAVED_NO; controller_back(&s);
    assert(!strcmp(s.context.selected.reference,"inputs/tidal/artists/1")&&s.context.saved==SAVED_YES);
    assert(!strcmp(s.context.filter,"artists")&&!strcmp(s.context.cursor,"opaque_cursor"));
    assert(controller_voice_start(&s,1001)); assert(s.voice==VOICE_RECORDING);
    assert(!controller_voice_tick(&s,31000)); assert(controller_voice_tick(&s,31001));
    assert(s.voice==VOICE_STOPPED&&!s.transcript[0]); /* no auto transcription */
    controller_snapshot(&s,32000); assert(controller_voice_start(&s,32001));
    assert(s.recording_until==62001); controller_push(&s,FIND);
    assert(s.voice==VOICE_IDLE&&!s.recording_until&&!s.transcript[0]);
    s.fixture=false; assert(!controller_voice_start(&s,32002));
    return 0;
}

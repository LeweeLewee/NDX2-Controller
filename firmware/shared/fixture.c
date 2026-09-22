/* Silent in-memory bridge for firmware before hardware/provisioning. */
#include "fixture.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static uint64_t (*clock_ms)(void);
static void (*diagnostic)(const char *);
static bool playing, pending, paused;
static uint32_t sequence;
static unsigned track_index;
static int position_ms;
static const char *track_titles[]={"Silent track","Silent track 2","Silent track 3"};
static const char *track_title(void) {
    return playing?track_titles[track_index]:"Silent fixture - ready";
}
static void track_ref(char out[257]) { snprintf(out,257,"inputs/tidal/tracks/%u",101+track_index); }
static bridge_reply_t result;
static int membership[4][32];
static unsigned kind_index(const char *ref) { return strstr(ref,"/artists/")?2:strstr(ref,"/tracks/")?1:strstr(ref,"/playlists/")?3:0; }
static unsigned item_index(const char *ref) { const char *p=strrchr(ref,'/'); return p?(unsigned)atoi(p+1)%32:0; }
static bool snapshot(controller_t *s) { strcpy(s->title,track_title()); strcpy(s->transport,paused?"paused":"playing"); s->position_ms=position_ms; controller_snapshot(s,clock_ms()); return true; }
static bool play(const char *candidate) {
    diagnostic("fixture_native_resolve_then_play_once"); playing=true; paused=false; track_index=0; position_ms=0;
    for(unsigned i=0;i<3;i++) {
        char ref[64]; snprintf(ref,sizeof(ref),"inputs/tidal/tracks/%u",101+i);
        if(candidate&&!strcmp(candidate,ref)) track_index=i;
    }
    return true;
}
static bool amp(bool up) { diagnostic(up?"fixture_amp_up_bounded":"fixture_amp_down_bounded"); return true; }
static bool light(bool on) { (void)on; diagnostic("backlight_not_bound"); return false; }
static bool sleep_mode(unsigned mode) { (void)mode; diagnostic("sleep_blocked_revision_audit_pending"); return false; }
static int battery(void) { return -1; }
static bool mic(void) { diagnostic("recording_fixture_no_capture"); return true; }
static void cancel(void) { diagnostic("capture_cancel_discard"); }
static void item(bridge_item_t *out,const char *ref) {
    memset(out,0,sizeof(*out)); snprintf(out->reference,sizeof(out->reference),"%s",ref);
    const char *kind=kind_index(ref)==2?"artists":kind_index(ref)==1?"tracks":kind_index(ref)==3?"playlists":"albums";
    strcpy(out->kind,kind); snprintf(out->title,sizeof(out->title),"Silent %s %u",kind,item_index(ref));
    strcpy(out->artist,"Fixture Ensemble"); strcpy(out->album,"Silent album");
    if(strcmp(kind,"artists")) strcpy(out->artist_reference,"inputs/tidal/artists/1");
    if(!strcmp(kind,"tracks")) strcpy(out->album_reference,"inputs/tidal/albums/1");
    for(unsigned i=0;i<3;i++) {
        char known[64]; snprintf(known,sizeof(known),"inputs/tidal/tracks/%u",101+i);
        if(!strcmp(ref,known)) strcpy(out->title,track_titles[i]);
    }
    out->saved=membership[kind_index(ref)][item_index(ref)];
}
static bool submit(const bridge_request_t *r) {
    if(pending) return false;
    memset(&result,0,sizeof(result)); result.valid=result.fixture=true; result.generation=r->generation;
    result.action=r->action; result.started_ms=r->started_ms; result.next_offset=-1; result.saved=-1;
    result.position_ms=position_ms; result.duration_ms=330000; result.bitrate=-1;
    result.outcome=bridge_mutation(r->action)?BR_SUBMITTED:BR_OBSERVED; result.valid_for_ms=5000;
    if(r->action==BR_SNAPSHOT) {
        strcpy(result.title,track_title()); strcpy(result.artist,"Fixture Ensemble"); strcpy(result.album,"Silent album");
        strcpy(result.source,"tidal"); strcpy(result.transport,paused?"paused":"playing"); strcpy(result.account,"fixture");
        char ref[257]; track_ref(ref);
        item(&result.item,ref); strcpy(result.item.title,track_title());
        result.items[0]=result.item; result.count=1;
    } else if(r->action==BR_SEARCH||r->action==BR_LIBRARY) {
        unsigned end=r->offset+12; if(end>29) end=29;
        for(unsigned n=r->offset;n<end;n++) {
            char ref[257]; snprintf(ref,sizeof(ref),"inputs/tidal/%s/%u",r->kind[0]?r->kind:"albums",n+1);
            item(&result.items[result.count],ref);
            if(r->action==BR_SEARCH||result.items[result.count].saved==1) result.count++;
        }
        result.next_offset=end<29?(int)end:-1; strcpy(result.result_id,"fixture");
    } else if(r->action==BR_BROWSE) {
        item(&result.item,r->text); result.playable=strcmp(result.item.kind,"artists")!=0;
        item(&result.items[0],!strcmp(result.item.kind,"artists")?"inputs/tidal/albums/1":"inputs/tidal/tracks/101"); result.count=1;
    } else if(r->action==BR_SAVED) result.saved=membership[kind_index(r->text)][item_index(r->text)];
    else if(r->action==BR_SAVE||r->action==BR_REMOVE) membership[kind_index(r->text)][item_index(r->text)]=r->action==BR_SAVE;
    else if(r->action==BR_PLAY) play(r->text);
    else if(r->action==BR_AMP_UP||r->action==BR_AMP_DOWN) amp(r->action==BR_AMP_UP);
    else if(r->action==BR_TRANSPORT) {
        diagnostic("fixture_transport_once");
        if(!strcmp(r->text,"pause")) paused=true;
        else if(!strcmp(r->text,"resume")) paused=false;
        else if(!strcmp(r->text,"next")||!strcmp(r->text,"prev")) {
            track_index=(track_index+(!strcmp(r->text,"next")?1:2))%3;
            playing=true; position_ms=0;
        }
    }
    else if(r->action==BR_VOICE) strcpy(result.transcript,"quiet instrumental albums");
    else if(r->action==BR_QUEUE) { char ref[257]; track_ref(ref); item(&result.items[0],ref); strcpy(result.items[0].title,track_title()); result.count=1; }
    pending=true; return true;
}
static bool poll_reply(bridge_reply_t *out) { if(!pending) return false; *out=result; pending=false; return true; }
static void invalidate(uint32_t generation) { (void)generation; pending=false; }
static void request_id(char out[49]) { snprintf(out,49,"silent_fixture_%032u",(unsigned)++sequence); }
platform_t fixture_platform(uint64_t (*now)(void),void (*log)(const char *)) {
    clock_ms=now; diagnostic=log; pending=playing=paused=false; track_index=0; position_ms=76000;
    for(unsigned k=0;k<4;k++) for(unsigned i=0;i<32;i++) membership[k][i]=i==1?0:-1;
    membership[1][101%32]=0;
    platform_t p={now,log,snapshot,play,amp,light,sleep_mode,battery,mic,cancel,submit,poll_reply,invalidate,request_id,NULL,NULL}; return p;
}

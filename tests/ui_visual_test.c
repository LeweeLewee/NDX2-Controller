/* Deterministic native visual review. Synthetic state only; no network/mutations. */
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../firmware/shared/ui.c"
static unsigned char pixels[800*480*3];
static uint64_t clock_now(void) { return 1000; }
static void noop(void) {}
static void log_noop(const char *s) { (void)s; }
static void flush_review(lv_disp_drv_t *d,const lv_area_t *a,lv_color_t *c) {
    for(int y=a->y1;y<=a->y2;y++) for(int x=a->x1;x<=a->x2;x++) {
        uint32_t rgb=lv_color_to32(*c++); unsigned n=(y*800+x)*3;
        pixels[n]=(rgb>>16)&255; pixels[n+1]=(rgb>>8)&255; pixels[n+2]=rgb&255;
    }
    lv_disp_flush_ready(d);
}
static lv_obj_t *action_widget(lv_obj_t *o,unsigned action) {
    if((uintptr_t)lv_obj_get_event_user_data(o,click)==action) return o;
    for(unsigned i=0;i<lv_obj_get_child_cnt(o);i++) { lv_obj_t *found=action_widget(lv_obj_get_child(o,i),action); if(found) return found; }
    return NULL;
}
static void shot(const char *dir,const char *name) {
    render(); lv_obj_update_layout(root); lv_refr_now(NULL);
    if(!strcmp(name,"01-sage")||!strcmp(name,"02-sand")||!strcmp(name,"03-slate"))
        printf("PALETTE %s %06x %06x %06x\n",name+3,(unsigned)background(),(unsigned)paper(),(unsigned)muted());
    if(state.context.screen==NOW) {
        unsigned actions[]={26,27,28,14,15}; int right=-1;
        for(unsigned i=0;i<5;i++) {
            lv_obj_t *o=action_widget(root,actions[i]); assert(o); lv_area_t a; lv_obj_get_coords(o,&a);
            assert(lv_obj_get_width(o)>=72&&lv_obj_get_height(o)>=64&&a.x1>right&&a.y2<400); right=a.x2;
            if(!state.online||state.busy) assert(lv_obj_has_state(o,LV_STATE_DISABLED));
        }
    }
    if(dir) {
        char path[1024]; snprintf(path,sizeof(path),"%s/%s.ppm",dir,name); FILE *f=fopen(path,"wb"); assert(f);
        fprintf(f,"P6\n800 480\n255\n"); assert(fwrite(pixels,1,sizeof(pixels),f)==sizeof(pixels)); fclose(f);
    }
}
int main(int argc,char **argv) {
    lv_init(); static lv_color_t buffer[800*40]; static lv_disp_draw_buf_t draw;
    lv_disp_draw_buf_init(&draw,buffer,NULL,800*40); static lv_disp_drv_t d; lv_disp_drv_init(&d);
    d.hor_res=800; d.ver_res=480; d.draw_buf=&draw; d.flush_cb=flush_review; lv_disp_drv_register(&d);
    platform_t platform={.now_ms=clock_now,.diagnostic=log_noop,.microphone_cancel=noop};
    io=&platform; controller_init(&state); root=lv_scr_act(); lv_obj_set_style_text_font(root,&lv_font_montserrat_20,0);
    state.online=true; state.fresh_until=10000; state.fixture=true; state.consume_contact=false;
    strcpy(state.title,"A Still Morning"); strcpy(state.artist,"River Stone Ensemble"); strcpy(state.album,"Listening Studies, Vol. 01");
    strcpy(state.source,"tidal"); strcpy(state.transport,"playing"); strcpy(state.account,"fixture");
    strcpy(state.current.reference,"inputs/tidal/tracks/101"); strcpy(state.current.artist_reference,"inputs/tidal/artists/1"); strcpy(state.current.album_reference,"inputs/tidal/albums/1");
    strcpy(state.current.artwork,"fixture:study0"); state.position_ms=76000; state.duration_ms=330000; state.bitrate=-1; state.track_saved=SAVED_NO;
    const char *dir=argc>1?argv[1]:NULL;
    shot(dir,"01-sage"); state.palette=1; shot(dir,"02-sand"); state.palette=2; shot(dir,"03-slate"); state.palette=0;
    strcpy(state.transport,"paused"); shot(dir,"04-paused"); strcpy(state.transport,"playing");
    strcpy(state.title,"An exceptionally long track title for a late evening listening session"); shot(dir,"05-long-title"); strcpy(state.title,"A Still Morning");
    state.current.artwork[0]=0; state.fixture=false; shot(dir,"06-missing-art");
    state.online=false; state.outcome=OUTCOME_UNKNOWN; shot(dir,"07-offline-unknown");
    state.online=true; state.fixture=true; state.outcome=OUTCOME_NONE; strcpy(state.current.artwork,"fixture:study0");
    state.busy=true; shot(dir,"08-pending"); state.busy=false;
    state.context.screen=FIND; strcpy(state.context.query,"Evening listening"); state.context.count=4;
    const char *titles[]={"A Still Morning","An exceptionally long album title for seated reading","Soft Light","Quiet Hours"};
    for(unsigned i=0;i<4;i++) { strcpy(state.context.items[i].title,titles[i]); strcpy(state.context.items[i].artist,"River Stone Ensemble"); strcpy(state.context.items[i].kind,"albums"); state.context.items[i].saved=(int)(i%3)-1; }
    shot(dir,"09-find"); state.context.screen=QUEUE; shot(dir,"10-queue");
    state.context.screen=SETTINGS; shot(dir,"11-settings"); state.context.screen=DISPLAY; shot(dir,"12-display");
    state.context.screen=DETAILS; state.context.selected=state.current; strcpy(state.context.selected.title,"Listening Studies, Vol. 01"); strcpy(state.context.selected.kind,"albums"); strcpy(state.context.selected.artist,"River Stone Ensemble"); state.context.playable=true;
    shot(dir,"13-detail");
    puts("PASS native visual state matrix and nonoverlapping transport targets; physical usability remains separate"); return 0;
}

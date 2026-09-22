/* SDL desktop runs exactly the shared LVGL renderer and controller state. */
#define SDL_MAIN_HANDLED
#include <SDL.h>
#include "lvgl.h"
#include "ui.h"
#include "fixture.h"
#include "transport.h"
#include "preferences_store.h"
#include <stdio.h>
#include <string.h>
static SDL_Renderer *renderer;
static SDL_Texture *texture;
static uint32_t pixels[800*480];
static lv_color_t draw_buffer[800*40];
static bool down;
static int px,py;
static uint64_t release_at, smoke_clock_offset;
static void tap(int x,int y) { px=x; py=y; down=true; release_at=SDL_GetTicks64()+smoke_clock_offset+90; }
static void capture(const char *directory,const char *name) {
    /* UI timers can update widgets after the display timer in the same pass. */
    lv_refr_now(NULL);
    char path[1024]; snprintf(path,sizeof(path),"%s/%s.bmp",directory,name);
    SDL_Surface *surface=SDL_CreateRGBSurfaceFrom(pixels,800,480,32,800*4,0x00ff0000,0x0000ff00,0x000000ff,0xff000000);
    if(surface) { SDL_SaveBMP(surface,path); SDL_FreeSurface(surface); }
}
static uint64_t now_ms(void) { return SDL_GetTicks64()+smoke_clock_offset; }
static void log_event(const char *event) { printf("%llu %s fixture=1\n",(unsigned long long)now_ms(),event); }
static void flush(lv_disp_drv_t *drv,const lv_area_t *area,lv_color_t *colors) {
    for(int y=area->y1;y<=area->y2;y++) for(int x=area->x1;x<=area->x2;x++) {
        uint32_t c=lv_color_to32(*colors++); if(x>=0&&x<800&&y>=0&&y<480) pixels[y*800+x]=c;
    }
    SDL_UpdateTexture(texture,NULL,pixels,800*4); SDL_RenderCopy(renderer,texture,NULL,NULL); SDL_RenderPresent(renderer);
    lv_disp_flush_ready(drv);
}
static void read_pointer(lv_indev_drv_t *drv,lv_indev_data_t *data) {
    (void)drv; data->point.x=px; data->point.y=py;
    data->state=down?LV_INDEV_STATE_PRESSED:LV_INDEV_STATE_RELEASED;
    if(!controller_ui_touch(down)) data->state=LV_INDEV_STATE_RELEASED;
}
int main(int argc,char **argv) {
    const char *smoke=NULL,*python=NULL,*config=NULL,*preferences_path=NULL,*preferences_smoke=NULL;
    bool transport_smoke=false;
    for(int i=1;i<argc;i++) {
        if(!strcmp(argv[i],"--smoke")&&i+1<argc) smoke=argv[++i];
        else if(!strcmp(argv[i],"--bridge")&&i+2<argc) { python=argv[++i]; config=argv[++i]; }
        else if(!strcmp(argv[i],"--preferences")&&i+1<argc) preferences_path=argv[++i];
        else if(!strcmp(argv[i],"--preferences-smoke")&&i+1<argc) preferences_smoke=argv[++i];
        else if(!strcmp(argv[i],"--transport-smoke")) transport_smoke=true;
        else return 2;
    }
    SDL_SetMainReady();
    if(SDL_Init(SDL_INIT_VIDEO|SDL_INIT_TIMER)!=0) return 1;
    SDL_Window *window=SDL_CreateWindow("NDX2 SILENT FIXTURE",SDL_WINDOWPOS_CENTERED,SDL_WINDOWPOS_CENTERED,800,480,smoke?SDL_WINDOW_HIDDEN:0);
    renderer=SDL_CreateRenderer(window,-1,SDL_RENDERER_SOFTWARE);
    texture=SDL_CreateTexture(renderer,SDL_PIXELFORMAT_ARGB8888,SDL_TEXTUREACCESS_STREAMING,800,480);
    lv_init(); static lv_disp_draw_buf_t draw; lv_disp_draw_buf_init(&draw,draw_buffer,NULL,800*40);
    static lv_disp_drv_t display; lv_disp_drv_init(&display); display.hor_res=800; display.ver_res=480;
    display.draw_buf=&draw; display.flush_cb=flush; lv_disp_drv_register(&display);
    static lv_indev_drv_t input; lv_indev_drv_init(&input); input.type=LV_INDEV_TYPE_POINTER; input.read_cb=read_pointer; lv_indev_drv_register(&input);
    platform_t platform=fixture_platform(now_ms,log_event);
    if(python&&!desktop_transport_init(&platform,python,config)) return 2;
    char default_preferences[1024];
    if(!preferences_path) {
        char *directory=SDL_GetPrefPath("NDX2","Controller");
        if(directory) { snprintf(default_preferences,sizeof(default_preferences),"%spreferences.bin",directory); SDL_free(directory); preferences_path=default_preferences; }
    }
    if(preferences_path) desktop_preferences_init(&platform,preferences_path);
    controller_ui_init(&platform);
    bool running=true; uint64_t last=now_ms(),started=last,next=last+2500; unsigned stage=0; int exit_code=0;
    while(running) {
        SDL_Event e; while(SDL_PollEvent(&e)) {
            if(e.type==SDL_QUIT) running=false;
            if(e.type==SDL_MOUSEBUTTONDOWN||e.type==SDL_MOUSEBUTTONUP) { down=e.type==SDL_MOUSEBUTTONDOWN; px=e.button.x; py=e.button.y; }
            if(e.type==SDL_MOUSEMOTION) { px=e.motion.x; py=e.motion.y; }
        }
        uint64_t now=now_ms(); lv_tick_inc((uint32_t)(now-last)); last=now; lv_timer_handler(); SDL_Delay(5);
        if(release_at&&now>=release_at) { down=false; release_at=0; }
        if(smoke&&now>=next) {
            const controller_t *s=controller_ui_state();
            next=now+500;
            if(transport_smoke) {
                if(controller_ui_ready()) {
                    if(stage==0&&!strcmp(s->transport,"playing")) { capture(smoke,"playing"); tap(433,350); stage++; }
                    else if(stage==1&&!strcmp(s->transport,"paused")) { capture(smoke,"paused"); tap(433,350); stage++; }
                    else if(stage==2&&!strcmp(s->transport,"playing")) { capture(smoke,"resumed"); tap(534,350); stage++; }
                    else if(stage==3&&!strcmp(s->current.reference,"inputs/tidal/tracks/102")&&s->position_ms==0) { capture(smoke,"next"); tap(332,350); stage++; }
                    else if(stage==4&&!strcmp(s->current.reference,"inputs/tidal/tracks/101")) { capture(smoke,"previous"); tap(332,350); stage++; }
                    else if(stage==5&&!strcmp(s->current.reference,"inputs/tidal/tracks/103")) { capture(smoke,"previous-wrap"); tap(534,350); stage++; }
                    else if(stage==6&&!strcmp(s->current.reference,"inputs/tidal/tracks/101")) { capture(smoke,"next-wrap"); puts("PASS native Play/Pause icons and Next/Previous track sequence"); running=false; }
                }
                if(SDL_GetTicks64()-started>20000) { fprintf(stderr,"Transport smoke timed out at stage %u\n",stage); exit_code=10; running=false; }
                continue;
            }
            if(preferences_smoke) {
                switch(stage) {
                case 0:
                    if(!strcmp(preferences_smoke,"check")&&(s->palette!=1||s->brightness!=65||s->timeout!=5)) { exit_code=7; running=false; break; }
                    tap(756,30); stage++; break;
                case 1: if(s->context.screen==SETTINGS) { tap(330,120); stage++; } break;
                case 2: if(s->context.screen==DISPLAY) {
                    if(!strcmp(preferences_smoke,"save")) { tap(400,210); stage++; }
                    else { capture(smoke,"15-preferences-restored"); puts("PASS preferences restored in fresh native process"); running=false; }
                } break;
                case 3: if(s->palette==1) {
                    /* Native value-change events from the actual Display widgets. */
                    lv_obj_t *body=lv_obj_get_child(lv_scr_act(),3);
                    lv_obj_t *slider=lv_obj_get_child(body,1), *dropdown=lv_obj_get_child(body,6);
                    lv_slider_set_value(slider,65,LV_ANIM_OFF); lv_event_send(slider,LV_EVENT_VALUE_CHANGED,NULL);
                    lv_dropdown_set_selected(dropdown,2); lv_event_send(dropdown,LV_EVENT_VALUE_CHANGED,NULL);
                    next=now+1200; stage++;
                } break;
                case 4:
                    if(s->brightness!=65||s->timeout!=5||!controller_ui_save_preferences()) { exit_code=8; running=false; break; }
                    capture(smoke,"14-preferences-saved"); puts("PASS preferences edited and saved through native UI"); running=false; break;
                }
                if(SDL_GetTicks64()-started>15000) { exit_code=9; running=false; }
                continue;
            }
            switch(stage) {
            case 0: if(controller_ui_ready()) { capture(smoke,"01-now"); tap(290,440); stage++; } break;
            case 1: if(s->context.screen==FIND) { tap(664,108); stage++; } break;
            case 2: if(s->context.count) { capture(smoke,"02-find"); tap(330,236); stage++; } break;
            case 3: if(s->context.screen==DETAILS&&controller_ui_ready()) { capture(smoke,"03-details"); tap(60,30); stage++; } break;
            case 4: if(s->context.screen==FIND) { if(s->context.count!=12) { exit_code=3; running=false; } tap(330,236); stage++; } break;
            case 5: if(s->context.screen==DETAILS&&controller_ui_ready()&&s->context.playable) { tap(310,356); stage++; } break;
            case 6: if(s->context.screen==NOW&&strstr(s->title,"Silent track")&&controller_ui_ready()) { capture(smoke,"04-playing"); tap(290,440); stage++; } break;
            case 7: if(s->context.screen==FIND&&controller_ui_ready()) { tap(744,108); stage++; } break;
            case 8: if(s->context.screen==VOICE&&s->voice==VOICE_RECORDING) { capture(smoke,"05-recording"); tap(390,292); stage++; } break;
            case 9: if(s->voice==VOICE_RECORDING) { tap(160,292); stage++; } break;
            case 10: if(s->context.screen==FIND&&s->context.count&&strstr(s->context.query,"quiet")) { capture(smoke,"06-voice-search"); tap(744,108); stage++; } break;
            case 11: if(s->voice==VOICE_RECORDING) { tap(620,292); stage++; } break;
            case 12: if(s->context.screen==FIND&&s->voice==VOICE_IDLE) { tap(756,30); stage++; } break;
            case 13: if(s->context.screen==SETTINGS) { capture(smoke,"07-settings"); tap(330,120); stage++; } break;
            case 14: if(s->context.screen==DISPLAY) { capture(smoke,"08-display"); tap(60,30); stage++; } break;
            case 15: if(s->context.screen==SETTINGS) { tap(100,440); stage++; } break;
            case 16: if(s->context.screen==NOW&&controller_ui_ready()) { tap(440,200); stage++; } break;
            case 17: if(s->context.screen==DETAILS&&controller_ui_ready()&&!strcmp(s->context.selected.kind,"artists")) {
                capture(smoke,"09-artist"); tap(640,140); stage++;
            } break;
            case 18: if(s->context.saved==SAVED_YES&&controller_ui_ready()) { capture(smoke,"10-following"); tap(60,30); stage++; } break;
            case 19: if(s->context.screen==NOW&&controller_ui_ready()) { tap(410,138); stage++; } break;
            case 20: if(s->context.screen==DETAILS&&controller_ui_ready()) {
                if(strcmp(s->context.selected.kind,"tracks")||s->context.saved!=SAVED_NO) { exit_code=5; running=false; break; }
                capture(smoke,"11-track"); tap(540,356); stage++;
            } break;
            case 21: if(s->context.saved==SAVED_YES&&controller_ui_ready()) { tap(290,440); stage++; } break;
            case 22: if(s->context.screen==FIND&&controller_ui_ready()) { tap(744,108); stage++; } break;
            case 23: if(s->voice==VOICE_RECORDING) { smoke_clock_offset+=30000; next=now_ms()+500; stage++; } break;
            case 24: if(s->voice==VOICE_STOPPED&&s->context.screen==VOICE) { capture(smoke,"12-voice-limit"); tap(620,292); stage++; } break;
            case 25: if(s->context.screen==FIND&&s->voice==VOICE_IDLE) {
                controller_ui_disconnect(); tap(100,440); stage++; break;
            } break;
            case 26: if(controller_ui_ready()) {
                if(s->context.screen!=FIND) { exit_code=6; running=false; break; }
                capture(smoke,"13-wake-restored"); puts("PASS native UI: details/Back/play/voice limit/restart/search/cancel/follow/library/settings/wake contact"); running=false;
            } break;
            }
            if(SDL_GetTicks64()-started>30000) { fprintf(stderr,"Native UI smoke timed out at stage %u\n",stage); exit_code=4; running=false; }
        }
    }
    controller_ui_save_preferences(); desktop_preferences_close();
    desktop_transport_close(); SDL_DestroyTexture(texture); SDL_DestroyRenderer(renderer); SDL_DestroyWindow(window); SDL_Quit(); return exit_code;
}

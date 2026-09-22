#include "ui.h"
#include "lvgl.h"
#include <stdio.h>
#include <string.h>

/* All widgets and controller state are owned by the LVGL task. */
static controller_t state;
static platform_t *io;
static lv_obj_t *content, *status, *query, *rows, *keyboard, *root;
static bool pressed_allowed, contact_active, network_pending, refresh_needed, dirty;
static bool check_saved_after, saved_is_track, browse_more;
static uint64_t next_read;
static unsigned backoff=1000;
static bridge_request_t request;
static bridge_reply_t reply;
static char membership_ref[257];
static bool last_ready, deferred_read;
static bridge_action_t deferred_action;
static char deferred_text[257];
static unsigned voice_second;
static void render(void);
static uint32_t background(void) { return state.palette==1?0x292620:state.palette==2?0x22282e:0x202521; }
static uint32_t accent(void) { return state.palette==1?0xddc8a6:state.palette==2?0xb9cddd:0xc2d1b5; }
const controller_t *controller_ui_state(void) { return &state; }
bool controller_ui_ready(void) { return controller_available(&state,io->now_ms())&&!network_pending; }
static void remember_scroll(void) { if(rows) state.context.scroll=lv_obj_get_scroll_y(rows); }
static void cancel_capture(void) { io->microphone_cancel(); controller_voice_cancel(&state); }
static void start_capture(void) {
    cancel_capture();
    if(controller_voice_start(&state,io->now_ms())&&!io->microphone_start()) controller_voice_cancel(&state);
}
static void abandon_read(void) {
    deferred_read=false;
    if(network_pending&&!state.busy) {
        state.generation++; if(io->invalidate) io->invalidate(state.generation); network_pending=false;
    }
}
static bool send_request(bridge_action_t action,const char *text) {
    if(!io->submit||network_pending) return false;
    if(bridge_mutation(action)&&!controller_available(&state,io->now_ms())) return false;
    memset(&request,0,sizeof(request)); request.action=action; request.generation=state.generation;
    request.started_ms=io->now_ms(); io->request_id(request.id);
    if(text) snprintf(request.text,sizeof(request.text),"%s",text);
    if(action==BR_BROWSE&&browse_more) request.offset=state.context.offset;
    if(action==BR_SEARCH||action==BR_LIBRARY||action==BR_QUEUE) {
        request.offset=state.context.offset;
        strcpy(request.kind,state.context.filter); strcpy(request.cursor,state.context.cursor);
        if(action==BR_SEARCH) strcpy(request.result_id,state.context.result_id);
    }
    if(!io->submit(&request)) {
        /* A cancelled generation may still occupy the transport worker. Retain
         * only the new read, never a mutation, until that worker is drained. */
        if(!bridge_mutation(action)&&action!=BR_SNAPSHOT) {
            deferred_read=true; deferred_action=action;
            snprintf(deferred_text,sizeof(deferred_text),"%s",request.text);
        }
        return false;
    }
    deferred_read=false;
    network_pending=true;
    if(bridge_mutation(action)) { state.busy=true; state.outcome=OUTCOME_PENDING; }
    return true;
}
static void reset_page(void) {
    rows=NULL; state.context.offset=0; state.context.scroll=0; state.context.cursor[0]=0;
    state.context.result_id[0]=0; state.context.next_offset=-1; state.context.count=0;
}
static void search_page(void) {
    send_request(state.context.screen==COLLECTION?BR_LIBRARY:state.context.screen==QUEUE?BR_QUEUE:BR_SEARCH,state.context.query);
}
static void membership(const char *reference,bool track) {
    snprintf(membership_ref,sizeof(membership_ref),"%s",reference); saved_is_track=track;
    if(reference[0]) send_request(BR_SAVED,reference);
}
bool controller_ui_touch(bool pressed) { contact_active=pressed; return controller_touch(&state,pressed); }
void controller_ui_disconnect(void) {
    deferred_read=false; cancel_capture(); controller_disconnect(&state);
    state.track_saved=state.context.saved=SAVED_UNKNOWN;
    if(io->invalidate) io->invalidate(state.generation);
    network_pending=false; refresh_needed=true; next_read=io->now_ms(); dirty=true;
}
static void keyboard_event(lv_event_t *e) {
    if(lv_event_get_code(e)==LV_EVENT_VALUE_CHANGED) {
        snprintf(state.context.query,sizeof(state.context.query),"%s",lv_textarea_get_text(query)); return;
    }
    if(lv_event_get_code(e)==LV_EVENT_FOCUSED&&!keyboard) {
        keyboard=lv_keyboard_create(root); lv_obj_set_size(keyboard,800,240);
        lv_obj_align(keyboard,LV_ALIGN_BOTTOM_MID,0,0); lv_keyboard_set_textarea(keyboard,query);
        lv_obj_add_event_cb(keyboard,keyboard_event,LV_EVENT_READY,NULL);
        lv_obj_add_event_cb(keyboard,keyboard_event,LV_EVENT_CANCEL,NULL);
    } else if(keyboard&&lv_event_get_code(e)!=LV_EVENT_FOCUSED) { lv_obj_del(keyboard); keyboard=NULL; dirty=true; }
}
static void open_ref(const char *reference) {
    if(!reference[0]||network_pending) return;
    remember_scroll(); browse_more=false; send_request(BR_BROWSE,reference);
}
static void click(lv_event_t *e) {
    if(lv_event_get_code(e)==LV_EVENT_PRESSED) { pressed_allowed=controller_ui_touch(true); return; }
    if(lv_event_get_code(e)==LV_EVENT_RELEASED) { controller_ui_touch(false); return; }
    if(lv_event_get_code(e)!=LV_EVENT_CLICKED||!pressed_allowed) return;
    unsigned a=(unsigned)(uintptr_t)lv_event_get_user_data(e);
    if(state.busy) return;
    if(keyboard) { lv_obj_del(keyboard); keyboard=NULL; }
    if(a<6||a==10||(a>=40&&a<=46)) {
        remember_scroll(); rows=NULL; abandon_read(); cancel_capture();
        if(a==10) controller_back(&state);
        else controller_push(&state,a>=40?(screen_t)(SETTINGS+a-40):(screen_t)a);
        if(a==FIND) {
            bool restored=false;
            for(unsigned n=state.depth;n>0;n--) if(state.history[n-1].screen==FIND) { state.context=state.history[n-1]; restored=true; break; }
            if(!restored) reset_page();
        }
        if(a==VOICE) start_capture();
        if(a==COLLECTION||a==QUEUE) { reset_page(); search_page(); }
    } else if(a==11) {
        snprintf(state.context.query,sizeof(state.context.query),"%s",lv_textarea_get_text(query));
        reset_page(); search_page();
    } else if(a==13&&controller_ui_ready()&&state.context.playable) {
        if(io->submit) send_request(BR_PLAY,state.context.selected.reference);
        else { io->native_play_once(state.context.selected.reference); io->snapshot(&state); controller_push(&state,NOW); }
    } else if((a==14||a==15)&&controller_ui_ready()) {
        if(io->submit) send_request(a==15?BR_AMP_UP:BR_AMP_DOWN,NULL);
        else io->amplifier_once(a==15);
    } else if(a==17) start_capture();
    else if(a==18&&(state.voice==VOICE_RECORDING||state.voice==VOICE_STOPPED)) {
        io->microphone_cancel(); state.voice=VOICE_STOPPED;
        if(io->submit) send_request(BR_VOICE,NULL);
        else { controller_back(&state); state.context.screen=FIND; strcpy(state.context.query,"quiet instrumental albums"); reset_page(); }
    } else if(a==19) { cancel_capture(); abandon_read(); controller_back(&state); }
    else if((a==21||a==25)&&strcmp(state.account,"disconnected")) {
        bool track=a==25; saved_t saved=track?state.track_saved:state.context.saved;
        const char *ref=track?state.current.reference:state.context.selected.reference;
        snprintf(membership_ref,sizeof(membership_ref),"%s",ref); saved_is_track=track;
        if(saved==SAVED_UNKNOWN) membership(ref,track);
        else if(io->submit) send_request(saved==SAVED_YES?BR_REMOVE:BR_SAVE,ref);
        else if(track) state.track_saved=saved==SAVED_YES?SAVED_NO:SAVED_YES;
        else state.context.saved=saved==SAVED_YES?SAVED_NO:SAVED_YES;
    } else if(a==24&&!network_pending) {
        if(state.context.next_offset>=0) state.context.offset=(unsigned)state.context.next_offset;
        else if(state.context.cursor[0]) state.context.offset=0; else return;
        state.context.scroll=0; rows=NULL;
        if(state.context.screen==DETAILS) { browse_more=true; send_request(BR_BROWSE,state.context.selected.reference); }
        else search_page();
    } else if(a>=26&&a<=28&&controller_ui_ready()) {
        send_request(BR_TRANSPORT,a==26?"prev":a==28?"next":!strcmp(state.transport,"playing")?"pause":"resume");
    } else if(a>=30&&a<=34) {
        bridge_item_t *item=state.context.screen==NOW?&state.current:&state.context.selected;
        open_ref(a==30?item->reference:a==31?item->artist_reference:item->album_reference);
    } else if(a>=50&&a<=53&&!network_pending) {
        const char *filters[]={"albums","tracks","artists","playlists"};
        strcpy(state.context.filter,filters[a-50]); reset_page(); search_page();
    } else if(a>=60&&a<=62) state.palette=a-60;
    else if(a==63) state.brightness=state.brightness>=100?30:state.brightness+10;
    else if(a==64) state.timeout=state.timeout==1?2:state.timeout==2?5:state.timeout==5?0:1;
    else if(a==65) { /* explicit simulated setup, never touches network credentials */
        io->diagnostic("fixture_wifi_setup_only"); controller_back(&state);
    } else if(a==66) { io->diagnostic("fixture_pairing_setup_only"); controller_back(&state); }
    else if(a==67) { controller_ui_disconnect(); io->diagnostic("wake_consume_contact"); }
    else if(a>=200&&a<200+state.context.count&&strcmp(state.account,"disconnected")) {
        bridge_item_t *item=&state.context.items[a-200];
        snprintf(membership_ref,sizeof(membership_ref),"%s",item->reference); saved_is_track=false;
        if(item->saved<0) send_request(BR_SAVED,membership_ref);
        else send_request(item->saved?BR_REMOVE:BR_SAVE,membership_ref);
    }
    else if(a>=100&&a<100+state.context.count) open_ref(state.context.items[a-100].reference);
    dirty=true;
}
static lv_obj_t *label(lv_obj_t *parent,const char *text,int x,int y,int w,int h,const lv_font_t *font) {
    lv_obj_t *o=lv_label_create(parent); lv_label_set_text(o,text); lv_obj_set_pos(o,x,y); lv_obj_set_size(o,w,h);
    lv_obj_set_style_text_font(o,font,0); lv_obj_set_style_text_color(o,lv_color_hex(0xe7e7da),0);
    lv_label_set_long_mode(o,LV_LABEL_LONG_DOT); return o;
}
static lv_obj_t *button(lv_obj_t *parent,const char *text,int x,int y,int w,int h,unsigned action,bool enabled,bool quiet) {
    lv_obj_t *o=lv_btn_create(parent); lv_obj_set_pos(o,x,y); lv_obj_set_size(o,w,h);
    lv_obj_set_style_radius(o,8,0); lv_obj_set_style_shadow_width(o,0,0); lv_obj_set_style_border_width(o,quiet?0:1,0);
    lv_obj_set_style_border_color(o,lv_color_hex(0x58664d),0); lv_obj_set_style_bg_color(o,lv_color_hex(0x323e2d),0);
    lv_obj_set_style_bg_opa(o,quiet?LV_OPA_TRANSP:LV_OPA_COVER,0); lv_obj_set_style_pad_all(o,4,0);
    lv_obj_set_style_text_color(o,lv_color_hex(accent()),0);
    lv_obj_add_event_cb(o,click,LV_EVENT_ALL,(void *)(uintptr_t)action);
    if(!enabled) lv_obj_add_state(o,LV_STATE_DISABLED);
    lv_obj_t *t=lv_label_create(o); lv_label_set_text(t,text); lv_obj_set_width(t,w-8);
    lv_label_set_long_mode(t,LV_LABEL_LONG_DOT); lv_obj_set_style_text_align(t,LV_TEXT_ALIGN_CENTER,0); lv_obj_center(t);
    return o;
}
static lv_obj_t *left_button(lv_obj_t *parent,const char *text,int x,int y,int w,int h,unsigned action,bool enabled) {
    lv_obj_t *o=button(parent,text,x,y,w,h,action,enabled,true);
    lv_obj_t *t=lv_obj_get_child(o,0); lv_obj_set_style_text_align(t,LV_TEXT_ALIGN_LEFT,0); lv_obj_align(t,LV_ALIGN_LEFT_MID,0,0); return o;
}
/* Small native line icon for heart: no external image/font dependency. */
static void heart_draw(lv_event_t *e) {
    lv_obj_t *o=lv_event_get_target(e); lv_area_t area; lv_obj_get_coords(o,&area);
    lv_draw_ctx_t *ctx=lv_event_get_draw_ctx(e); lv_draw_line_dsc_t d; lv_draw_line_dsc_init(&d);
    d.color=lv_color_hex(accent()); d.width=2;
    static const lv_point_t p[]={{0,7},{2,2},{7,0},{12,5},{17,0},{22,2},{24,7},{22,12},{12,23},{2,12},{0,7}};
    for(unsigned i=1;i<sizeof(p)/sizeof(p[0]);i++) {
        lv_point_t a={area.x1+20+p[i-1].x,area.y1+16+p[i-1].y},b={area.x1+20+p[i].x,area.y1+16+p[i].y};
        lv_draw_line(ctx,&d,&a,&b);
    }
}
static void search_draw(lv_event_t *e) {
    lv_area_t a; lv_obj_get_coords(lv_event_get_target(e),&a); lv_draw_ctx_t *ctx=lv_event_get_draw_ctx(e);
    lv_draw_arc_dsc_t d; lv_draw_arc_dsc_init(&d); d.color=lv_color_hex(accent()); d.width=2;
    lv_point_t center={a.x1+28,a.y1+27}; lv_draw_arc(ctx,&d,&center,10,0,360);
    lv_draw_line_dsc_t l; lv_draw_line_dsc_init(&l); l.color=d.color; l.width=2;
    lv_point_t p={a.x1+36,a.y1+35},q={a.x1+46,a.y1+45}; lv_draw_line(ctx,&l,&p,&q);
}
static void mic_draw(lv_event_t *e) {
    lv_area_t a; lv_obj_get_coords(lv_event_get_target(e),&a); lv_draw_ctx_t *ctx=lv_event_get_draw_ctx(e);
    lv_draw_rect_dsc_t d; lv_draw_rect_dsc_init(&d); d.bg_opa=LV_OPA_TRANSP; d.border_width=2;
    d.border_color=lv_color_hex(accent()); d.radius=6;
    lv_area_t r={a.x1+26,a.y1+14,a.x1+38,a.y1+36}; lv_draw_rect(ctx,&d,&r);
    lv_draw_arc_dsc_t arc; lv_draw_arc_dsc_init(&arc); arc.color=d.border_color; arc.width=2;
    lv_point_t center={a.x1+32,a.y1+31}; lv_draw_arc(ctx,&arc,&center,12,0,180);
    lv_draw_line_dsc_t l; lv_draw_line_dsc_init(&l); l.color=d.border_color; l.width=2;
    lv_point_t p={a.x1+32,a.y1+43},q={a.x1+32,a.y1+51}; lv_draw_line(ctx,&l,&p,&q);
}
static void art(int size) {
    lv_obj_t *o=lv_obj_create(content); lv_obj_set_pos(o,0,0); lv_obj_set_size(o,size,size);
    lv_obj_set_style_bg_color(o,lv_color_hex(0x2b322b),0); lv_obj_set_style_border_color(o,lv_color_hex(0x58634e),0);
    lv_obj_clear_flag(o,LV_OBJ_FLAG_SCROLLABLE);
    label(o,"Artwork\nunavailable",12,size/2-40,size-48,80,&lv_font_montserrat_20);
}
static void filters(void) {
    const char *names[]={"Albums","Tracks","Artists","Playlists"}; const char *keys[]={"albums","tracks","artists","playlists"};
    for(unsigned i=0;i<4;i++) button(content,names[i],i*188,76,180,44,50+i,!network_pending,strcmp(state.context.filter,keys[i])!=0);
}
static void list_rows(int y,int height,bool actionable) {
    rows=lv_obj_create(content); lv_obj_set_pos(rows,0,y); lv_obj_set_size(rows,752,height);
    lv_obj_set_style_pad_all(rows,0,0); lv_obj_set_style_border_width(rows,0,0); lv_obj_set_style_bg_opa(rows,LV_OPA_TRANSP,0);
    for(unsigned i=0;i<state.context.count;i++) {
        bridge_item_t *item=&state.context.items[i];
        left_button(rows,item->title,0,i*76,650,70,100+i,actionable&&!network_pending);
        if(actionable) button(rows,item->saved==1?LV_SYMBOL_OK:item->saved==0?LV_SYMBOL_PLUS:"?",674,i*76,72,70,200+i,controller_ui_ready()&&strcmp(state.account,"disconnected"),true);
    }
    if(!state.context.count) label(rows,network_pending?"Loading...":"No items available",0,12,700,40,&lv_font_montserrat_20);
    if(state.context.next_offset>=0||state.context.cursor[0]) button(rows,"More",0,state.context.count*76,720,60,24,!network_pending,true);
    lv_obj_scroll_to_y(rows,state.context.scroll,LV_ANIM_OFF);
}
static void display_setting(lv_event_t *e) {
    unsigned kind=(unsigned)(uintptr_t)lv_event_get_user_data(e);
    if(kind==1) {
        state.brightness=(unsigned)lv_slider_get_value(lv_event_get_target(e));
        char text[96]; snprintf(text,sizeof(text),"Brightness: %u%% / fixture preference",state.brightness);
        lv_label_set_text(lv_obj_get_child(content,0),text);
    } else {
        const unsigned minutes[]={1,2,5,0}; state.timeout=minutes[lv_dropdown_get_selected(lv_event_get_target(e))];
    }
}
static void render(void) {
    if(keyboard) { lv_obj_del(keyboard); keyboard=NULL; }
    lv_obj_clean(root); rows=query=NULL; dirty=false;
    bool ready=controller_ui_ready(); last_ready=ready;
    bool library_ready=ready&&strcmp(state.account,"disconnected");
    lv_obj_set_style_bg_color(root,lv_color_hex(background()),0);
    button(root,state.context.screen==NOW?"NDX 2":LV_SYMBOL_LEFT " Back",16,4,112,52,10,state.depth>0,true);
    status=label(root,"",144,22,580,28,&lv_font_montserrat_16);
    char text[768]; snprintf(text,sizeof(text),"%s  |  %s  |  Battery unavailable",state.fixture?"FIXTURE":"Bridge",
        state.busy?"Pending":state.outcome==OUTCOME_UNKNOWN?"Outcome unknown":ready?"Connected":state.online?"Checking / stale":"Offline");
    lv_label_set_text(status,text);
    button(root,LV_SYMBOL_SETTINGS,728,4,56,52,40,true,true);
    content=lv_obj_create(root); lv_obj_set_pos(content,24,76); lv_obj_set_size(content,752,312);
    lv_obj_set_style_pad_all(content,0,0); lv_obj_set_style_border_width(content,0,0); lv_obj_set_style_bg_opa(content,LV_OPA_TRANSP,0);
    lv_obj_clear_flag(content,LV_OBJ_FLAG_SCROLLABLE);
    const char *nav[]={LV_SYMBOL_AUDIO " Playing","Find",LV_SYMBOL_LIST " Collection",LV_SYMBOL_BARS " Queue"};
    const unsigned actions[]={NOW,FIND,COLLECTION,QUEUE};
    screen_t section=state.context.screen;
    if(section==VOICE) section=FIND;
    if(section==DETAILS&&state.depth) { section=state.history[state.depth-1].screen; if(section==DETAILS) section=FIND; }
    for(unsigned i=0;i<4;i++) button(root,nav[i],20+i*192,408,184,64,actions[i],true,section!=actions[i]);
    switch(state.context.screen) {
    case NOW: {
        art(240);
        snprintf(text,sizeof(text),"%s / %s",state.source[0]?state.source:"Source unavailable",state.transport[0]?state.transport:"unknown");
        label(content,text,268,0,254,24,&lv_font_montserrat_16);
        if(state.bitrate>0) snprintf(text,sizeof(text),"%d kbps",state.bitrate); else strcpy(text,"Bitrate unavailable");
        label(content,text,532,0,220,24,&lv_font_montserrat_16);
        lv_obj_t *title=left_button(content,state.title,268,28,408,68,30,state.current.reference[0]&&!network_pending);
        lv_obj_set_style_text_font(title,&lv_font_montserrat_32,0);
        lv_obj_t *heart=button(content,state.track_saved==SAVED_UNKNOWN?"?":state.track_saved==SAVED_YES?LV_SYMBOL_OK:"",684,28,64,64,25,library_ready&&state.current.reference[0],true);
        lv_obj_add_event_cb(heart,heart_draw,LV_EVENT_DRAW_MAIN_END,NULL);
        left_button(content,state.artist[0]?state.artist:"Artist unavailable",268,102,484,42,31,state.current.artist_reference[0]&&!network_pending);
        left_button(content,state.album[0]?state.album:"Album unavailable",268,148,484,42,32,state.current.album_reference[0]&&!network_pending);
        lv_obj_t *bar=lv_bar_create(content); lv_obj_set_pos(bar,268,202); lv_obj_set_size(bar,484,3);
        lv_bar_set_value(bar,state.duration_ms>0&&state.position_ms>=0?(int)((int64_t)state.position_ms*100/state.duration_ms):0,LV_ANIM_OFF);
        lv_obj_set_style_bg_color(bar,lv_color_hex(accent()),LV_PART_INDICATOR);
        if(state.position_ms>=0) snprintf(text,sizeof(text),"%d:%02d",state.position_ms/60000,state.position_ms/1000%60); else strcpy(text,"--:--");
        label(content,text,268,214,100,24,&lv_font_montserrat_16);
        if(state.duration_ms>=0) snprintf(text,sizeof(text),"%d:%02d",state.duration_ms/60000,state.duration_ms/1000%60); else strcpy(text,"--:--");
        label(content,text,690,214,62,24,&lv_font_montserrat_16);
        const char *icons[]={LV_SYMBOL_PREV,!strcmp(state.transport,"playing")?LV_SYMBOL_PAUSE:LV_SYMBOL_PLAY,LV_SYMBOL_NEXT,LV_SYMBOL_VOLUME_MID " -",LV_SYMBOL_VOLUME_MID " +"};
        const unsigned acts[]={26,27,28,14,15};
        for(unsigned i=0;i<5;i++) { lv_obj_t *control=button(content,icons[i],268+i*101,242,80,64,acts[i],ready,true); lv_obj_set_style_text_font(control,&lv_font_montserrat_32,0); }
        break; }
    case FIND:
        query=lv_textarea_create(content); lv_obj_set_pos(query,0,0); lv_obj_set_size(query,596,64);
        lv_textarea_set_one_line(query,true); lv_textarea_set_max_length(query,256); lv_textarea_set_text(query,state.context.query);
        lv_obj_set_style_bg_color(query,lv_color_hex(0x303b2d),0); lv_obj_set_style_text_color(query,lv_color_hex(0xe7e7da),0);
        lv_obj_add_event_cb(query,keyboard_event,LV_EVENT_FOCUSED,NULL); lv_obj_add_event_cb(query,keyboard_event,LV_EVENT_VALUE_CHANGED,NULL);
        lv_obj_t *search=button(content,"",608,0,64,64,11,!network_pending,true);
        lv_obj_add_event_cb(search,search_draw,LV_EVENT_DRAW_MAIN_END,NULL);
        lv_obj_t *mic=button(content,"",688,0,64,64,VOICE,ready&&state.fixture,true);
        lv_obj_add_event_cb(mic,mic_draw,LV_EVENT_DRAW_MAIN_END,NULL);
        filters(); list_rows(128,184,true); break;
    case COLLECTION:
        label(content,!strcmp(state.account,"disconnected")?"Connect your collection on the bridge computer":"Your collection",0,8,740,48,&lv_font_montserrat_24);
        filters(); list_rows(128,184,true); break;
    case DETAILS: {
        bridge_item_t *item=&state.context.selected; bool artist=!strcmp(item->kind,"artists");
        if(artist) {
            label(content,"ARTIST / TIDAL",0,0,480,24,&lv_font_montserrat_16);
            label(content,item->title,0,32,472,76,&lv_font_montserrat_32);
            label(content,state.context.saved==SAVED_YES?"Following":state.context.saved==SAVED_NO?"Not following":"Follow status unknown",0,112,480,32,&lv_font_montserrat_20);
            button(content,state.context.saved==SAVED_YES?"Unfollow artist":state.context.saved==SAVED_NO?"Follow artist":"? Follow status",490,30,262,72,21,library_ready,false);
            list_rows(160,152,true); break;
        }
        art(200); label(content,item->kind[0]?item->kind:"Native item",226,0,510,28,&lv_font_montserrat_16);
        label(content,item->title,226,32,526,88,&lv_font_montserrat_24);
        left_button(content,item->artist[0]?item->artist:"Artist unavailable",226,124,526,40,31,item->artist_reference[0]&&!network_pending);
        left_button(content,item->album,226,168,526,40,32,item->album_reference[0]&&!network_pending);
        const char *saved=state.context.saved==SAVED_YES?(artist?"Following":"In your library"):state.context.saved==SAVED_NO?(artist?"Not following":"Not in your library"):"Library status unknown";
        label(content,saved,226,218,526,28,&lv_font_montserrat_16);
        if(!artist) button(content,"Play",226,252,170,60,13,ready&&state.context.playable,false);
        const char *action=artist?(state.context.saved==SAVED_YES?"Unfollow artist":state.context.saved==SAVED_NO?"Follow artist":"? Follow status"):
            state.context.saved==SAVED_YES?LV_SYMBOL_OK " Library":state.context.saved==SAVED_NO?LV_SYMBOL_PLUS " Library":"? Library";
        button(content,action,artist?226:410,252,artist?300:260,60,21,library_ready,false);
        lv_obj_add_flag(content,LV_OBJ_FLAG_SCROLLABLE); rows=content;
        for(unsigned i=0;i<state.context.count;i++) button(content,state.context.items[i].title,0,332+i*72,736,64,100+i,!network_pending,true);
        if(state.context.next_offset>=0) button(content,"More",0,332+state.context.count*72,736,60,24,!network_pending,true);
        lv_obj_scroll_to_y(content,state.context.scroll,LV_ANIM_OFF); break; }
    case QUEUE: list_rows(0,312,false); break;
    case VOICE:
        label(content,state.voice==VOICE_RECORDING?"Listening...":state.voice==VOICE_STOPPED?"Recording stopped":"Microphone unavailable",24,8,704,44,&lv_font_montserrat_24);
        label(content,"Say an artist, album or the kind of music you want.",24,64,700,64,&lv_font_montserrat_20);
        snprintf(text,sizeof(text),"%u / 30 seconds",state.voice==VOICE_IDLE?0:(unsigned)(30-(state.recording_until>io->now_ms()?(state.recording_until-io->now_ms()+999)/1000:0)));
        label(content,text,24,130,700,36,&lv_font_montserrat_24);
        button(content,"Stop & search",24,184,264,64,18,!network_pending&&state.voice!=VOICE_IDLE,false);
        button(content,"Restart",300,184,188,64,17,ready&&state.fixture,false); button(content,"Cancel",500,184,196,64,19,true,true);
        label(content,"Microphone fixture: no audio captured. Search only.",24,270,704,40,&lv_font_montserrat_16); break;
    case SETTINGS:
        button(content,"Display   /   Brightness, appearance and timeout",0,0,752,94,41,true,true);
        button(content,"Connection   /   Wi-Fi, bridge and pairing",0,104,752,94,42,true,true);
        button(content,"Device   /   Battery, software and diagnostics",0,208,752,94,43,true,true); break;
    case DISPLAY: {
        snprintf(text,sizeof(text),"Brightness: %u%% / fixture preference",state.brightness);
        label(content,text,0,0,752,36,&lv_font_montserrat_20);
        lv_obj_t *slider=lv_slider_create(content); lv_obj_set_pos(slider,16,54); lv_obj_set_size(slider,716,12);
        lv_slider_set_range(slider,30,100); lv_slider_set_value(slider,state.brightness,LV_ANIM_OFF);
        lv_obj_set_style_bg_color(slider,lv_color_hex(accent()),LV_PART_INDICATOR);
        lv_obj_set_style_bg_color(slider,lv_color_hex(accent()),LV_PART_KNOB);
        lv_obj_add_event_cb(slider,display_setting,LV_EVENT_VALUE_CHANGED,(void *)1);
        button(content,"Sage",0,102,240,64,60,true,state.palette!=0); button(content,"Sand",256,102,240,64,61,true,state.palette!=1); button(content,"Slate",512,102,240,64,62,true,state.palette!=2);
        label(content,"Turn screen off after",0,216,480,36,&lv_font_montserrat_20);
        lv_obj_t *timeout=lv_dropdown_create(content); lv_obj_set_pos(timeout,500,202); lv_obj_set_size(timeout,252,56);
        lv_dropdown_set_options(timeout,"1 minute\n2 minutes\n5 minutes\nNever");
        lv_dropdown_set_selected(timeout,state.timeout==1?0:state.timeout==2?1:state.timeout==5?2:3);
        lv_obj_add_event_cb(timeout,display_setting,LV_EVENT_VALUE_CHANGED,(void *)2);
        label(content,"Session fixtures only. Hardware brightness / sleep unavailable.",0,278,752,34,&lv_font_montserrat_16); break; }
    case CONNECTION:
        button(content,"Wi-Fi   /   Setup fixture",0,0,752,78,44,state.fixture,true);
        button(content,"Bridge   /   Pairing setup",0,88,752,78,45,true,true);
        label(content,"Music accounts: manage sign-in on the bridge computer.\nTrust and device authorization are required.",16,194,720,100,&lv_font_montserrat_20); break;
    case DEVICE:
        label(content,"Battery: unavailable\nSoftware: shared native C / LVGL\nMicrophone and sleep: hardware unavailable",0,0,752,148,&lv_font_montserrat_20);
        button(content,"Simulate wake / reconnect",0,174,420,64,67,state.fixture,false);
        label(content,"Fixture diagnostics only; no flash, reset or update.",0,270,752,40,&lv_font_montserrat_16); break;
    case WIFI:
        label(content,"Wi-Fi setup fixture\nNo network or password is changed.",0,0,752,120,&lv_font_montserrat_24);
        button(content,"Simulate connection",0,170,380,64,65,state.fixture,false); break;
    case PAIRING:
        label(content,"Provision trust and approve the controller\nthrough local bridge administration.\nNo real code or credential is collected here.",0,0,752,160,&lv_font_montserrat_20);
        button(content,"Simulate pairing",0,190,320,64,66,state.fixture,false); break;
    }
    if(state.error_code[0]) lv_label_set_text(status,state.error_code);
}
static void apply_reply(void) {
    network_pending=false;
    snprintf(state.error_code,sizeof(state.error_code),"%s",reply.valid?reply.error_code:"BRIDGE_UNAVAILABLE");
    if(bridge_mutation(reply.action)) {
        remember_scroll();
        state.busy=false; state.online=false; state.fresh_until=0;
        state.outcome=reply.valid&&reply.outcome==BR_SUBMITTED?OUTCOME_SUBMITTED:reply.valid&&reply.outcome==BR_REJECTED?OUTCOME_NONE:OUTCOME_UNKNOWN;
        refresh_needed=true; next_read=0;
        check_saved_after=reply.action==BR_SAVE||reply.action==BR_REMOVE;
        if(check_saved_after) { if(saved_is_track) state.track_saved=SAVED_UNKNOWN; else state.context.saved=SAVED_UNKNOWN; }
        if(reply.action==BR_PLAY) { rows=NULL; controller_push(&state,NOW); }
    }
    if(!reply.valid||reply.outcome==BR_REJECTED) {
        if(reply.action==BR_SAVED) { if(saved_is_track) state.track_saved=SAVED_UNKNOWN; else state.context.saved=SAVED_UNKNOWN; }
        else if(!bridge_mutation(reply.action)) { cancel_capture(); controller_disconnect(&state); io->invalidate(state.generation); }
        next_read=io->now_ms()+backoff; backoff=backoff<15000?backoff*2:30000;
    } else if(reply.outcome==BR_OBSERVED) {
        state.fixture=reply.fixture; backoff=1000;
        if(reply.action==BR_SNAPSHOT) {
            bool changed=strcmp(state.current.reference,reply.item.reference)!=0;
            state.online=true; state.fresh_until=reply.started_ms+reply.valid_for_ms;
            strcpy(state.title,reply.title); strcpy(state.artist,reply.artist); strcpy(state.album,reply.album);
            strcpy(state.source,reply.source); strcpy(state.transport,reply.transport); strcpy(state.account,reply.account);
            state.current=reply.item; state.position_ms=reply.position_ms; state.duration_ms=reply.duration_ms; state.bitrate=reply.bitrate;
            if(state.context.screen==QUEUE&&state.context.offset==0) {
                state.context.count=reply.count; memcpy(state.context.items,reply.items,sizeof(state.context.items));
            }
            next_read=io->now_ms()+2000; refresh_needed=false;
            if(changed) state.track_saved=SAVED_UNKNOWN;
            if(check_saved_after) { check_saved_after=false; send_request(BR_SAVED,membership_ref); }
            else if(changed&&state.current.reference[0]) membership(state.current.reference,true);
        } else if(reply.action==BR_SEARCH||reply.action==BR_LIBRARY||reply.action==BR_QUEUE) {
            state.context.count=reply.count; memcpy(state.context.items,reply.items,sizeof(state.context.items));
            state.context.next_offset=reply.next_offset; strcpy(state.context.result_id,reply.result_id);
            if(reply.next_offset<0) strcpy(state.context.cursor,reply.cursor);
        } else if(reply.action==BR_BROWSE) {
            rows=NULL;
            if(!browse_more) { controller_push(&state,DETAILS); reset_page(); state.context.saved=SAVED_UNKNOWN; }
            state.context.selected=reply.item; state.context.playable=reply.playable;
            state.context.count=reply.count; memcpy(state.context.items,reply.items,sizeof(state.context.items)); state.context.next_offset=reply.next_offset;
            browse_more=false; membership(state.context.selected.reference,false);
        } else if(reply.action==BR_SAVED) {
            saved_t value=reply.saved<0?SAVED_UNKNOWN:reply.saved?SAVED_YES:SAVED_NO;
            if(!strcmp(membership_ref,state.current.reference)) state.track_saved=value;
            if(!strcmp(membership_ref,state.context.selected.reference)) state.context.saved=value;
            /* Update retained list and detail membership, never their position/query. */
            for(unsigned h=0;h<=state.depth;h++) {
                context_t *c=h==state.depth?&state.context:&state.history[h];
                if(!strcmp(c->selected.reference,membership_ref)) c->saved=value;
                for(unsigned i=0;i<c->count;i++) if(!strcmp(c->items[i].reference,membership_ref)) c->items[i].saved=reply.saved;
            }
        } else if(reply.action==BR_VOICE) {
            cancel_capture(); controller_back(&state); state.context.screen=FIND;
            strcpy(state.context.query,reply.transcript); reset_page(); send_request(BR_SEARCH,state.context.query);
        }
    }
    dirty=true;
}
static void tick(lv_timer_t *timer) {
    (void)timer;
    remember_scroll();
    if(state.voice==VOICE_RECORDING&&voice_second!=io->now_ms()/1000) { voice_second=(unsigned)(io->now_ms()/1000); dirty=true; }
    if(controller_voice_tick(&state,io->now_ms())) { io->microphone_cancel(); dirty=true; }
    if(io->submit) {
        if(io->poll(&reply)&&reply.generation==state.generation) apply_reply();
        if(!network_pending&&!contact_active&&deferred_read) send_request(deferred_action,deferred_text);
        if(!network_pending&&!deferred_read&&!contact_active&&io->now_ms()>=next_read&&state.voice!=VOICE_RECORDING) send_request(BR_SNAPSHOT,NULL);
    } else io->snapshot(&state);
    if(last_ready!=controller_ui_ready()) dirty=true;
    if(dirty&&!keyboard&&!contact_active) { render(); }
}
void controller_ui_init(platform_t *platform) {
    io=platform; controller_init(&state); io->diagnostic("boot_controller");
    if(!io->submit) io->snapshot(&state); else { refresh_needed=true; next_read=0; }
    root=lv_scr_act(); lv_obj_set_style_text_font(root,&lv_font_montserrat_20,0);
    render(); lv_timer_create(tick,50,NULL);
}

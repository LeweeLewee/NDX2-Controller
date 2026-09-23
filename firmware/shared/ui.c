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
static char bridge_boot[81];
static bool last_ready, deferred_read;
static bridge_action_t deferred_action;
static char deferred_text[257];
static unsigned voice_second;
static lv_obj_t *preferences_label;
static bool preferences_pending, preferences_storage_available;
static uint64_t preferences_due;
static enum { SETTINGS_DEFAULTS, SETTINGS_SAVED, SETTINGS_PENDING, SETTINGS_FAILED, SETTINGS_UNAVAILABLE } preferences_status;
static void preferences_feedback(void) {
    if(!preferences_label) return;
    const char *messages[]={"Defaults; changes save locally.","Saved on this controller.","Saving preferences...",
        "Could not save; change a setting to retry.","Storage unavailable; session preferences only."};
    char text[160]; snprintf(text,sizeof(text),"%s\nBrightness / sleep hardware unavailable.",messages[preferences_status]);
    lv_label_set_text(preferences_label,text);
}
static void preferences_changed(void) {
    if(!preferences_storage_available) { preferences_status=SETTINGS_UNAVAILABLE; preferences_feedback(); return; }
    preferences_pending=true; preferences_due=io->now_ms()+750;
    preferences_status=SETTINGS_PENDING; preferences_feedback();
}
bool controller_ui_save_preferences(void) {
    if(!preferences_pending) return preferences_status!=SETTINGS_FAILED&&preferences_status!=SETTINGS_UNAVAILABLE;
    preferences_t p={state.palette,state.brightness,state.timeout};
    bool ok=io->save_preferences&&io->save_preferences(&p);
    preferences_pending=false; preferences_status=ok?SETTINGS_SAVED:SETTINGS_FAILED;
    preferences_feedback(); return ok;
}
static char artwork_target[81];
static uint64_t artwork_until;
static bool artwork_loaded, artwork_attempted;
static lv_color_t artwork_pixels[BRIDGE_ART_PIXELS];
static lv_img_dsc_t artwork_image;
static lv_obj_t *artwork_widget;
static const char *wanted_artwork(void) {
    if(!state.online||io->now_ms()>=state.fresh_until) return "";
    if(state.context.screen==NOW) return state.current.artwork;
    if(state.context.screen==DETAILS&&strcmp(state.context.selected.kind,"artists")) return state.context.selected.artwork;
    return "";
}
static void clear_artwork(void) {
    artwork_loaded=artwork_attempted=false; artwork_target[0]=0; artwork_until=0;
    if(artwork_widget) lv_obj_add_flag(artwork_widget,LV_OBJ_FLAG_HIDDEN);
    lv_img_cache_invalidate_src(&artwork_image); dirty=true;
}
static void sync_artwork(void) {
    const char *wanted=wanted_artwork();
    if(strcmp(artwork_target,wanted)||(artwork_until&&io->now_ms()>=artwork_until)) {
        clear_artwork(); snprintf(artwork_target,sizeof(artwork_target),"%s",wanted);
    }
}
static void render(void);
static uint32_t background(void) { return state.palette==1?0x292620:state.palette==2?0x22282e:0x202521; }
static uint32_t surface(void) { return state.palette==1?0x363026:state.palette==2?0x2c3741:0x2b342b; }
static uint32_t divider(void) { return state.palette==1?0x51483a:state.palette==2?0x43515e:0x3b4537; }
static uint32_t muted(void) { return state.palette==1?0xb8aa93:state.palette==2?0xa3b5c4:0x9eae96; }
static uint32_t paper(void) { return state.palette==1?0xeee2cf:state.palette==2?0xe0e7ed:0xe6eddd; }
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
        if(!bridge_mutation(action)&&action!=BR_SNAPSHOT&&action!=BR_ARTWORK) {
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
    deferred_read=pressed_allowed=check_saved_after=browse_more=false;
    clear_artwork(); cancel_capture(); controller_disconnect(&state);
    state.track_saved=SAVED_UNKNOWN;
    for(unsigned h=0;h<=state.depth;h++) {
        context_t *c=h==state.depth?&state.context:&state.history[h];
        c->saved=SAVED_UNKNOWN; c->selected.saved=-1;
        for(unsigned i=0;i<c->count;i++) c->items[i].saved=-1;
    }
    if(io->invalidate) io->invalidate(state.generation);
    network_pending=false; refresh_needed=true; next_read=io->now_ms(); dirty=true;
}
static void keyboard_event(lv_event_t *e) {
    if(lv_event_get_code(e)==LV_EVENT_VALUE_CHANGED) {
        snprintf(state.context.query,sizeof(state.context.query),"%s",lv_textarea_get_text(query)); return;
    }
    if(lv_event_get_code(e)==LV_EVENT_FOCUSED&&!keyboard) {
        keyboard=lv_keyboard_create(root); lv_obj_set_size(keyboard,800,240);
        lv_obj_set_style_bg_color(keyboard,lv_color_hex(background()),0);
        lv_obj_set_style_bg_color(keyboard,lv_color_hex(surface()),LV_PART_ITEMS);
        lv_obj_set_style_text_color(keyboard,lv_color_hex(paper()),LV_PART_ITEMS);
        lv_obj_set_style_bg_color(keyboard,lv_color_hex(accent()),LV_PART_ITEMS|LV_STATE_PRESSED);
        lv_obj_set_style_text_color(keyboard,lv_color_hex(background()),LV_PART_ITEMS|LV_STATE_PRESSED);
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
    } else if(a==17) { abandon_read(); start_capture(); }
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
    } else if(a>=60&&a<=62) { state.palette=a-60; preferences_changed(); }
    else if(a==63) { state.brightness=state.brightness>=100?30:state.brightness+10; preferences_changed(); }
    else if(a==64) { state.timeout=state.timeout==1?2:state.timeout==2?5:state.timeout==5?0:1; preferences_changed(); }
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
    lv_obj_set_style_text_font(o,font,0); lv_obj_set_style_text_color(o,lv_color_hex(paper()),0);
    lv_label_set_long_mode(o,LV_LABEL_LONG_DOT); return o;
}
static lv_obj_t *button(lv_obj_t *parent,const char *text,int x,int y,int w,int h,unsigned action,bool enabled,bool quiet) {
    lv_obj_t *o=lv_btn_create(parent); lv_obj_set_pos(o,x,y); lv_obj_set_size(o,w,h);
    lv_obj_set_style_radius(o,8,0); lv_obj_set_style_shadow_width(o,0,0); lv_obj_set_style_border_width(o,quiet?0:1,0);
    lv_obj_set_style_border_color(o,lv_color_hex(divider()),0); lv_obj_set_style_bg_color(o,lv_color_hex(surface()),0);
    lv_obj_set_style_bg_opa(o,quiet?LV_OPA_TRANSP:LV_OPA_COVER,0); lv_obj_set_style_pad_all(o,4,0);
    lv_obj_set_style_text_color(o,lv_color_hex(paper()),0);
    lv_obj_set_style_bg_color(o,lv_color_hex(surface()),LV_STATE_PRESSED);
    lv_obj_set_style_bg_opa(o,LV_OPA_COVER,LV_STATE_PRESSED);
    lv_obj_set_style_outline_color(o,lv_color_hex(accent()),LV_STATE_FOCUS_KEY);
    lv_obj_set_style_outline_width(o,2,LV_STATE_FOCUS_KEY);
    lv_obj_set_style_opa(o,LV_OPA_40,LV_STATE_DISABLED);
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
#include "ui_visual.h"
static void art(int size) {
    lv_obj_t *frame=lv_obj_create(content); lv_obj_remove_style_all(frame); lv_obj_clear_flag(frame,LV_OBJ_FLAG_CLICKABLE|LV_OBJ_FLAG_SCROLLABLE);
    lv_obj_set_pos(frame,0,0); lv_obj_set_size(frame,size,size); lv_obj_set_style_radius(frame,6,0);
    lv_obj_set_style_clip_corner(frame,true,0);
    if(artwork_loaded&&!strcmp(artwork_target,wanted_artwork())&&io->now_ms()<artwork_until) {
        artwork_widget=lv_img_create(frame);
        lv_img_set_src(artwork_widget,&artwork_image); lv_img_set_pivot(artwork_widget,0,0);
        lv_img_set_zoom(artwork_widget,(uint16_t)(size*256/BRIDGE_ART_SIDE));
        lv_obj_set_pos(artwork_widget,0,0); return;
    }
    lv_obj_t *o=frame;
    lv_obj_set_style_bg_color(o,lv_color_hex(surface()),0); lv_obj_set_style_border_color(o,lv_color_hex(divider()),0);
    lv_obj_set_style_border_width(o,1,0); lv_obj_set_style_radius(o,6,0); lv_obj_set_style_pad_all(o,0,0);
    lv_obj_clear_flag(o,LV_OBJ_FLAG_SCROLLABLE);
    lv_obj_t *mark=lv_obj_create(o); lv_obj_remove_style_all(mark); lv_obj_clear_flag(mark,LV_OBJ_FLAG_CLICKABLE); lv_obj_set_style_text_color(mark,lv_color_hex(muted()),0); lv_obj_set_size(mark,56,56);
    lv_obj_align(mark,LV_ALIGN_CENTER,0,-26); lv_obj_add_event_cb(mark,icon_draw,LV_EVENT_DRAW_MAIN_END,(void *)ICON_DISC);
    lv_obj_t *caption=label(o,"Artwork unavailable",8,size/2+24,size-16,48,&lv_font_montserrat_16);
    lv_obj_set_style_text_align(caption,LV_TEXT_ALIGN_CENTER,0); lv_obj_set_style_text_color(caption,lv_color_hex(muted()),0);
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
        rule(rows,0,i*76,746);
        lv_obj_t *row=left_button(rows,item->title,0,i*76,650,70,100+i,actionable&&!network_pending);
        /* Read-only queue rows remain fully legible, without becoming tappable. */
        if(!actionable) lv_obj_set_style_opa(row,LV_OPA_COVER,LV_STATE_DISABLED);
        lv_obj_t *title_label=lv_obj_get_child(row,0); lv_obj_set_align(title_label,LV_ALIGN_TOP_LEFT); lv_obj_set_pos(title_label,12,6); lv_obj_set_size(title_label,622,26);
        char subtitle[384]; snprintf(subtitle,sizeof(subtitle),"%s%s%s",item->artist,item->artist[0]?"  /  ":"",item->kind);
        lv_obj_t *sub=label(row,subtitle,12,38,622,22,&lv_font_montserrat_16); lv_obj_set_style_text_color(sub,lv_color_hex(muted()),0);
        if(actionable) icon_button(rows,item->saved==1?ICON_CHECK:item->saved==0?ICON_PLUS:ICON_QUESTION,674,i*76,72,70,200+i,controller_ui_ready()&&strcmp(state.account,"disconnected"));
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
    preferences_changed();
}
static void render(void) {
    if(keyboard) { lv_obj_del(keyboard); keyboard=NULL; }
    lv_obj_clean(root); preferences_label=NULL; artwork_widget=NULL; rows=query=NULL; dirty=false;
    bool ready=controller_ui_ready(); last_ready=ready;
    bool library_ready=ready&&strcmp(state.account,"disconnected");
    lv_obj_set_style_bg_color(root,lv_color_hex(background()),0);
    if(state.context.screen==NOW) {
        lv_obj_t *brand=label(root,"NDX 2",24,21,112,28,&lv_font_montserrat_20);
        lv_obj_set_style_text_letter_space(brand,2,0);
    } else left_button(root,LV_SYMBOL_LEFT "  Back",20,4,112,52,10,state.depth>0);
    status=label(root,"",168,24,548,24,&lv_font_montserrat_16);
    lv_obj_set_style_text_align(status,LV_TEXT_ALIGN_RIGHT,0);
    lv_obj_set_style_text_color(status,lv_color_hex(muted()),0);
    char text[768]; snprintf(text,sizeof(text),"%s%s",state.fixture?"Silent demo  /  ":"",
        state.busy?"Pending":state.outcome==OUTCOME_UNKNOWN?"Outcome unknown":(state.online&&io->now_ms()<state.fresh_until)?"Connected":state.online?"Checking connection":"Offline");
    lv_label_set_text(status,text);
    icon_button(root,ICON_SETTINGS,728,4,56,52,40,true);
    rule(root,24,63,752);
    content=lv_obj_create(root); lv_obj_set_pos(content,24,76); lv_obj_set_size(content,752,312);
    lv_obj_set_style_pad_all(content,0,0); lv_obj_set_style_border_width(content,0,0); lv_obj_set_style_bg_opa(content,LV_OPA_TRANSP,0);
    lv_obj_clear_flag(content,LV_OBJ_FLAG_SCROLLABLE);
    const char *nav[]={"Playing","Find","Collection","Queue"};
    const unsigned nav_icons[]={ICON_NOW,ICON_SEARCH,ICON_COLLECTION,ICON_QUEUE};
    const unsigned actions[]={NOW,FIND,COLLECTION,QUEUE};
    screen_t section=state.context.screen;
    if(section==VOICE) section=FIND;
    if(section==DETAILS&&state.depth) { section=state.history[state.depth-1].screen; if(section==DETAILS) section=FIND; }
    lv_obj_t *nav_bg=lv_obj_create(root); lv_obj_remove_style_all(nav_bg); lv_obj_set_pos(nav_bg,0,400); lv_obj_set_size(nav_bg,800,80);
    lv_obj_set_style_bg_color(nav_bg,lv_color_hex(state.palette==1?0x211f1a:state.palette==2?0x1b2128:0x1b211c),0);
    lv_obj_set_style_bg_opa(nav_bg,LV_OPA_COVER,0); rule(root,0,400,800);
    for(unsigned i=0;i<4;i++) {
        lv_obj_t *b=button(root,nav[i],20+i*192,408,184,64,actions[i],true,section!=actions[i]);
        lv_obj_set_style_border_width(b,0,0);
        lv_obj_t *t=lv_obj_get_child(b,0); lv_obj_set_width(t,132); lv_obj_align(t,LV_ALIGN_CENTER,15,0);
        lv_obj_set_style_text_color(b,lv_color_hex(section==actions[i]?paper():muted()),0);
        lv_obj_t *ic=lv_obj_create(b); lv_obj_remove_style_all(ic); lv_obj_clear_flag(ic,LV_OBJ_FLAG_CLICKABLE); lv_obj_set_size(ic,26,26); lv_obj_set_pos(ic,8,15);
        lv_obj_add_event_cb(ic,icon_draw,LV_EVENT_DRAW_MAIN_END,(void *)(uintptr_t)nav_icons[i]);
        if(section==actions[i]) { lv_obj_t *line=rule(b,16,57,144); lv_obj_set_style_bg_color(line,lv_color_hex(accent()),0); }
    }
    switch(state.context.screen) {
    case NOW: {
        art(240);
        snprintf(text,sizeof(text),"%s / %s",state.source[0]?state.source:"Source unavailable",!strcmp(state.transport,"playing")?"NOW PLAYING":!strcmp(state.transport,"paused")?"PAUSED":"UNKNOWN");
        lv_obj_t *kicker=label(content,text,268,0,264,24,&lv_font_montserrat_16); lv_obj_set_style_text_color(kicker,lv_color_hex(muted()),0);
        if(state.bitrate>0) snprintf(text,sizeof(text),"%d kbps",state.bitrate); else strcpy(text,"Bitrate unavailable");
        lv_obj_t *quality=label(content,text,532,0,220,24,&lv_font_montserrat_16); lv_obj_set_style_text_align(quality,LV_TEXT_ALIGN_RIGHT,0); lv_obj_set_style_text_color(quality,lv_color_hex(muted()),0);
        lv_obj_t *title=left_button(content,state.title,268,28,408,68,30,state.current.reference[0]&&!network_pending);
        lv_obj_set_style_text_font(title,&lv_font_montserrat_32,0); lv_obj_set_style_text_letter_space(title,-1,0);
        lv_obj_t *heart=icon_button(content,state.track_saved==SAVED_YES?ICON_HEART_SAVED:ICON_HEART,684,28,64,64,25,library_ready&&state.current.reference[0]);
        if(state.track_saved==SAVED_UNKNOWN) label(heart,"?",42,0,16,20,&lv_font_montserrat_16);
        lv_obj_t *artist_link=left_button(content,state.artist[0]?state.artist:"Artist unavailable",268,102,484,42,31,state.current.artist_reference[0]&&!network_pending);
        lv_obj_set_style_text_font(artist_link,&lv_font_montserrat_24,0);
        lv_obj_t *album=left_button(content,state.album[0]?state.album:"Album unavailable",268,148,484,42,32,state.current.album_reference[0]&&!network_pending);
        lv_obj_set_style_text_color(album,lv_color_hex(muted()),0);
        lv_obj_t *bar=lv_bar_create(content); lv_obj_set_pos(bar,268,202); lv_obj_set_size(bar,484,3);
        lv_bar_set_value(bar,state.duration_ms>0&&state.position_ms>=0?(int)((int64_t)state.position_ms*100/state.duration_ms):0,LV_ANIM_OFF);
        lv_obj_set_style_bg_color(bar,lv_color_hex(accent()),LV_PART_INDICATOR);
        lv_obj_set_style_bg_color(bar,lv_color_hex(divider()),0); lv_obj_set_style_bg_opa(bar,LV_OPA_COVER,0);
        if(state.position_ms>=0) snprintf(text,sizeof(text),"%d:%02d",state.position_ms/60000,state.position_ms/1000%60); else strcpy(text,"--:--");
        label(content,text,268,214,100,24,&lv_font_montserrat_16);
        if(state.duration_ms>=0) snprintf(text,sizeof(text),"%d:%02d",state.duration_ms/60000,state.duration_ms/1000%60); else strcpy(text,"--:--");
        label(content,text,690,214,62,24,&lv_font_montserrat_16);
        const unsigned icons[]={ICON_PREVIOUS,!strcmp(state.transport,"playing")?ICON_PAUSE:ICON_PLAY,ICON_NEXT,ICON_VOLUME_DOWN,ICON_VOLUME_UP};
        const unsigned acts[]={26,27,28,14,15};
        for(unsigned i=0;i<5;i++) icon_button(content,icons[i],268+i*101,242,80,64,acts[i],ready);
        break; }
    case FIND:
        query=lv_textarea_create(content); lv_obj_set_pos(query,0,0); lv_obj_set_size(query,596,64);
        lv_textarea_set_one_line(query,true); lv_textarea_set_max_length(query,256); lv_textarea_set_text(query,state.context.query);
        lv_obj_set_style_bg_color(query,lv_color_hex(surface()),0); lv_obj_set_style_text_color(query,lv_color_hex(paper()),0);
        lv_obj_add_event_cb(query,keyboard_event,LV_EVENT_FOCUSED,NULL); lv_obj_add_event_cb(query,keyboard_event,LV_EVENT_VALUE_CHANGED,NULL);
        lv_obj_t *search=button(content,"",608,0,64,64,11,!network_pending,true);
        lv_obj_add_event_cb(search,icon_draw,LV_EVENT_DRAW_MAIN_END,(void *)ICON_SEARCH);
        lv_obj_t *mic=button(content,"",688,0,64,64,VOICE,ready&&state.fixture,true);
        lv_obj_add_event_cb(mic,icon_draw,LV_EVENT_DRAW_MAIN_END,(void *)ICON_MIC);
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
        if(!artist) { lv_obj_t *play=button(content,"Play",226,252,170,60,13,ready&&state.context.playable,false);
            lv_obj_set_style_bg_color(play,lv_color_hex(accent()),0); lv_obj_set_style_text_color(play,lv_color_hex(background()),0); }
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
        button(content,"Restart",300,184,188,64,17,controller_available(&state,io->now_ms())&&state.fixture,false); button(content,"Cancel",500,184,196,64,19,true,true);
        label(content,"Microphone fixture: no audio captured. Search only.",24,270,704,40,&lv_font_montserrat_16); break;
    case SETTINGS:
        setting_row("Display","Brightness, appearance and screen timeout",0,41);
        setting_row("Connection","Wi-Fi, bridge and pairing",104,42);
        setting_row("Device","Battery, software and diagnostics",208,43); break;
    case DISPLAY: {
        snprintf(text,sizeof(text),"Brightness: %u%% / fixture preference",state.brightness);
        label(content,text,0,0,752,36,&lv_font_montserrat_20);
        lv_obj_t *slider=lv_slider_create(content); lv_obj_set_pos(slider,16,54); lv_obj_set_size(slider,716,12);
        lv_slider_set_range(slider,30,100); lv_slider_set_value(slider,state.brightness,LV_ANIM_OFF);
        lv_obj_set_style_bg_color(slider,lv_color_hex(divider()),LV_PART_MAIN);
        lv_obj_set_style_bg_color(slider,lv_color_hex(accent()),LV_PART_INDICATOR);
        lv_obj_set_style_bg_color(slider,lv_color_hex(accent()),LV_PART_KNOB);
        lv_obj_add_event_cb(slider,display_setting,LV_EVENT_VALUE_CHANGED,(void *)1);
        button(content,"Sage",0,102,240,64,60,true,state.palette!=0); button(content,"Sand",256,102,240,64,61,true,state.palette!=1); button(content,"Slate",512,102,240,64,62,true,state.palette!=2);
        label(content,"Turn screen off after",0,216,480,36,&lv_font_montserrat_20);
        lv_obj_t *timeout=lv_dropdown_create(content); lv_obj_set_pos(timeout,500,202); lv_obj_set_size(timeout,252,56);
        lv_dropdown_set_options(timeout,"1 minute\n2 minutes\n5 minutes\nNever");
        lv_obj_set_style_bg_color(timeout,lv_color_hex(surface()),0); lv_obj_set_style_text_color(timeout,lv_color_hex(paper()),0);
        lv_obj_set_style_border_color(timeout,lv_color_hex(divider()),0); lv_obj_set_style_border_width(timeout,1,0);
        lv_obj_t *options=lv_dropdown_get_list(timeout);
        lv_obj_set_style_bg_color(options,lv_color_hex(surface()),0); lv_obj_set_style_text_color(options,lv_color_hex(paper()),0);
        lv_obj_set_style_border_color(options,lv_color_hex(divider()),0);
        lv_obj_set_style_bg_color(options,lv_color_hex(accent()),LV_PART_SELECTED);
        lv_obj_set_style_text_color(options,lv_color_hex(background()),LV_PART_SELECTED);
        lv_dropdown_set_selected(timeout,state.timeout==1?0:state.timeout==2?1:state.timeout==5?2:3);
        lv_obj_add_event_cb(timeout,display_setting,LV_EVENT_VALUE_CHANGED,(void *)2);
        preferences_label=label(content,"",0,268,752,44,&lv_font_montserrat_16); preferences_feedback(); break; }
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
    if(state.error_code[0]) { lv_label_set_text(status,state.error_code); lv_obj_set_style_text_color(status,lv_color_hex(0xe0bc87),0); }
}
static void apply_reply(void) {
    network_pending=false;
    if(reply.valid&&reply.boot_id[0]) {
        bool restarted=bridge_boot[0]&&strcmp(bridge_boot,reply.boot_id);
        snprintf(bridge_boot,sizeof(bridge_boot),"%s",reply.boot_id);
        if(restarted) {
            controller_ui_disconnect();
            /* A reply from a new process cannot complete old interaction intent. */
            if(reply.action!=BR_SNAPSHOT) { dirty=true; return; }
        }
    }
    if(reply.valid&&reply.action==BR_SNAPSHOT&&reply.outcome==BR_OBSERVED&&
       reply.started_ms+reply.valid_for_ms<=io->now_ms()) {
        reply.valid=false;
    }
    if(reply.action==BR_ARTWORK) {
        sync_artwork();
        if(!strcmp(request.text,artwork_target)&&artwork_target[0]) {
            artwork_attempted=true; artwork_until=io->now_ms()+5000;
            if(reply.valid&&reply.outcome==BR_OBSERVED&&reply.artwork_available&&
               !strcmp(reply.artwork,artwork_target)&&reply.started_ms+reply.valid_for_ms>io->now_ms()) {
                lv_img_cache_invalidate_src(&artwork_image);
                for(unsigned i=0;i<BRIDGE_ART_PIXELS;i++) {
                    uint16_t c=reply.pixels[i];
                    artwork_pixels[i]=lv_color_make((uint8_t)(((c>>11)*255)/31),
                        (uint8_t)((((c>>5)&63)*255)/63),(uint8_t)(((c&31)*255)/31));
                }
                memset(&artwork_image,0,sizeof(artwork_image));
                artwork_image.header.cf=LV_IMG_CF_TRUE_COLOR;
                artwork_image.header.w=artwork_image.header.h=BRIDGE_ART_SIDE;
                artwork_image.data=(const uint8_t *)artwork_pixels; artwork_image.data_size=sizeof(artwork_pixels);
                artwork_loaded=true; artwork_until=reply.started_ms+reply.valid_for_ms;
            }
        }
        dirty=true; return; /* Optional artwork failure never disconnects playback. */
    }
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
        else if(!bridge_mutation(reply.action)) controller_ui_disconnect();
        next_read=io->now_ms()+backoff; backoff=backoff<15000?backoff*2:30000;
    } else if(reply.outcome==BR_OBSERVED) {
        state.fixture=reply.fixture; backoff=1000;
        if(reply.action==BR_SNAPSHOT) {
            bool changed=strcmp(state.current.reference,reply.item.reference)!=0;
            state.online=true; state.fresh_until=reply.started_ms+reply.valid_for_ms;
            strcpy(state.title,reply.title); strcpy(state.artist,reply.artist); strcpy(state.album,reply.album);
            strcpy(state.source,reply.source); strcpy(state.transport,reply.transport); strcpy(state.account,reply.account);
            state.current=reply.item; strcpy(state.current.artwork,reply.artwork); state.position_ms=reply.position_ms; state.duration_ms=reply.duration_ms; state.bitrate=reply.bitrate;
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
    if(preferences_pending&&!contact_active&&io->now_ms()>=preferences_due) controller_ui_save_preferences();
    if(state.voice==VOICE_RECORDING&&voice_second!=io->now_ms()/1000) { voice_second=(unsigned)(io->now_ms()/1000); dirty=true; }
    if(controller_voice_tick(&state,io->now_ms())) { io->microphone_cancel(); dirty=true; }
    if(io->submit) {
        if(io->poll(&reply)&&reply.generation==state.generation) apply_reply();
        if(network_pending&&io->now_ms()-request.started_ms>=8000) {
            controller_ui_disconnect();
            strcpy(state.error_code,"BRIDGE_UNAVAILABLE"); next_read=io->now_ms()+backoff;
            backoff=backoff<15000?backoff*2:30000;
        }
        sync_artwork();
        if(!network_pending&&!contact_active&&deferred_read) send_request(deferred_action,deferred_text);
        if(!network_pending&&!deferred_read&&!contact_active&&io->now_ms()>=next_read) send_request(BR_SNAPSHOT,NULL);
        if(!network_pending&&!deferred_read&&!contact_active&&artwork_target[0]&&!artwork_attempted&&state.voice!=VOICE_RECORDING) {
            if(send_request(BR_ARTWORK,artwork_target)) artwork_attempted=true;
        }
    } else io->snapshot(&state);
    if(last_ready!=controller_ui_ready()) dirty=true;
    if(dirty&&!keyboard&&!contact_active) { render(); }
}
void controller_ui_init(platform_t *platform) {
    io=platform; controller_init(&state); io->diagnostic("boot_controller");
    preferences_t preferences; preferences_defaults(&preferences);
    preferences_result_t loaded=io->load_preferences?io->load_preferences(&preferences):PREF_UNAVAILABLE;
    preferences_status=loaded==PREF_LOADED?SETTINGS_SAVED:loaded==PREF_DEFAULTS?SETTINGS_DEFAULTS:SETTINGS_UNAVAILABLE;
    if(loaded!=PREF_UNAVAILABLE&&preferences_valid(&preferences)) {
        state.palette=preferences.palette; state.brightness=preferences.brightness; state.timeout=preferences.timeout;
    } else preferences_status=SETTINGS_UNAVAILABLE;
    preferences_pending=false; preferences_storage_available=preferences_status!=SETTINGS_UNAVAILABLE&&io->save_preferences;
    if(!io->submit) io->snapshot(&state); else { refresh_needed=true; next_read=0; }
    root=lv_scr_act(); lv_obj_set_style_text_font(root,&lv_font_montserrat_20,0);
    render(); lv_timer_create(tick,50,NULL);
}

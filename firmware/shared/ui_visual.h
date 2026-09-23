/* Native vector marks derived from the approved 24-unit outline icon language.
 * No bitmap assets, font glyph substitutions or per-frame allocations. */
enum { ICON_PREVIOUS=1, ICON_PAUSE, ICON_PLAY, ICON_NEXT, ICON_VOLUME_DOWN,
    ICON_VOLUME_UP, ICON_SEARCH, ICON_MIC, ICON_SETTINGS, ICON_NOW,
    ICON_COLLECTION, ICON_QUEUE, ICON_HEART, ICON_HEART_SAVED,
    ICON_PLUS, ICON_CHECK, ICON_QUESTION, ICON_DISC };
static void icon_path(lv_draw_ctx_t *ctx,lv_draw_line_dsc_t *d,int x,int y,int size,const int8_t *p,unsigned n) {
    for(unsigned i=2;i<n;i+=2) {
        lv_point_t a={x+p[i-2]*size/24,y+p[i-1]*size/24},b={x+p[i]*size/24,y+p[i+1]*size/24};
        lv_draw_line(ctx,d,&a,&b);
    }
}
static void icon_draw(lv_event_t *e) {
    lv_obj_t *o=lv_event_get_target(e); lv_area_t a; lv_obj_get_coords(o,&a);
    unsigned icon=(unsigned)(uintptr_t)lv_event_get_user_data(e);
    int size=lv_obj_get_width(o)<40?24:30;
    if(icon==ICON_DISC) size=48;
    int x=a.x1+(lv_obj_get_width(o)-size)/2,y=a.y1+(lv_obj_get_height(o)-size)/2;
    lv_draw_ctx_t *ctx=lv_event_get_draw_ctx(e);
    lv_draw_line_dsc_t d; lv_draw_line_dsc_init(&d); d.color=lv_obj_get_style_text_color(o,0);
    d.width=2; d.round_start=d.round_end=1; d.opa=lv_obj_get_style_opa_recursive(o,0);
    lv_draw_arc_dsc_t arc; lv_draw_arc_dsc_init(&arc); arc.color=d.color; arc.width=2; arc.opa=d.opa;
#define PATH(...) do { const int8_t p[]={__VA_ARGS__}; icon_path(ctx,&d,x,y,size,p,sizeof(p)); } while(0)
#define CIRCLE(cx,cy,r) do { lv_point_t c={x+(cx)*size/24,y+(cy)*size/24}; lv_draw_arc(ctx,&arc,&c,(r)*size/24,0,360); } while(0)
    switch(icon) {
    case ICON_PREVIOUS: PATH(5,5,5,19); PATH(19,5,9,12,19,19,19,5); break;
    case ICON_NEXT: PATH(19,5,19,19); PATH(5,5,15,12,5,19,5,5); break;
    case ICON_PAUSE: PATH(9,5,9,19); PATH(15,5,15,19); break;
    case ICON_PLAY: PATH(8,5,19,12,8,19,8,5); break;
    case ICON_VOLUME_DOWN: case ICON_VOLUME_UP:
        PATH(11,5,6,9,3,9,3,15,6,15,11,19,11,5); PATH(16,12,22,12);
        if(icon==ICON_VOLUME_UP) { PATH(19,9,19,15); } break;
    case ICON_SEARCH: CIRCLE(10,10,6); PATH(15,15,21,21); break;
    case ICON_MIC: {
        lv_draw_rect_dsc_t r; lv_draw_rect_dsc_init(&r); r.bg_opa=LV_OPA_TRANSP;
        r.border_color=d.color; r.border_width=2; r.border_opa=d.opa; r.radius=4;
        lv_area_t box={x+9*size/24,y+3*size/24,x+15*size/24,y+15*size/24}; lv_draw_rect(ctx,&r,&box);
        lv_point_t c={x+size/2,y+12*size/24}; lv_draw_arc(ctx,&arc,&c,7*size/24,0,180);
        PATH(5,11,5,12); PATH(19,11,19,12); PATH(12,19,12,22); break; }
    case ICON_SETTINGS:
        PATH(9,3,15,3,16,6,19,7,21,12,19,17,16,18,15,21,9,21,8,18,5,17,3,12,5,7,8,6,9,3); CIRCLE(12,12,3); break;
    case ICON_NOW: PATH(5,10,5,14); PATH(10,5,10,19); PATH(15,8,15,16); PATH(20,11,20,13); break;
    case ICON_COLLECTION: PATH(4,4,10,4,10,20,4,20,4,4); PATH(14,5,19,4,22,19,17,20,14,5); break;
    case ICON_QUEUE: PATH(4,6,20,6); PATH(4,12,20,12); PATH(4,18,14,18); break;
    case ICON_HEART: case ICON_HEART_SAVED:
        PATH(12,21,3,12,2,10,2,7,3,5,5,4,8,4,10,5,12,7,14,5,16,4,19,4,21,5,22,7,22,10,21,12,12,21);
        if(icon==ICON_HEART_SAVED) { PATH(7,11,11,15,17,9); } break;
    case ICON_PLUS: PATH(12,5,12,19); PATH(5,12,19,12); break;
    case ICON_CHECK: PATH(5,12,9,16,19,6); break;
    case ICON_QUESTION: CIRCLE(12,12,9); PATH(9,8,10,6,14,6,15,8,15,10,12,12,12,14); PATH(12,17,12,18); break;
    case ICON_DISC: CIRCLE(12,12,10); CIRCLE(12,12,3); PATH(7,7,9,5); PATH(15,19,17,17); break;
    }
#undef PATH
#undef CIRCLE
}
static lv_obj_t *icon_button(lv_obj_t *parent,unsigned icon,int x,int y,int w,int h,unsigned action,bool enabled) {
    lv_obj_t *o=button(parent,"",x,y,w,h,action,enabled,true);
    lv_obj_set_style_text_color(o,lv_color_hex(accent()),0);
    lv_obj_add_event_cb(o,icon_draw,LV_EVENT_DRAW_MAIN_END,(void *)(uintptr_t)icon); return o;
}
static lv_obj_t *rule(lv_obj_t *parent,int x,int y,int width) {
    lv_obj_t *o=lv_obj_create(parent); lv_obj_remove_style_all(o); lv_obj_clear_flag(o,LV_OBJ_FLAG_CLICKABLE); lv_obj_set_pos(o,x,y); lv_obj_set_size(o,width,1);
    lv_obj_set_style_bg_color(o,lv_color_hex(divider()),0); lv_obj_set_style_bg_opa(o,LV_OPA_COVER,0); return o;
}
static void setting_row(const char *title,const char *subtitle,int y,unsigned action) {
    lv_obj_t *o=button(content,"",0,y,752,94,action,true,true);
    label(o,title,12,10,664,32,&lv_font_montserrat_24);
    lv_obj_t *sub=label(o,subtitle,12,48,664,28,&lv_font_montserrat_16);
    lv_obj_set_style_text_color(sub,lv_color_hex(muted()),0);
    label(o,LV_SYMBOL_RIGHT,710,28,26,30,&lv_font_montserrat_20); rule(content,0,y+93,752);
}

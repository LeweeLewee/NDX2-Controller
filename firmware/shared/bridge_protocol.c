#include "bridge_protocol.h"
#include "cJSON.h"
#include <string.h>
#include <stdio.h>
#include <math.h>
static const char *actions[]={"snapshot","search","browse","play","amplifier","amplifier","queue","library_state","library_save","library_save","transport","library_page","voice_review","artwork"};
bool bridge_mutation(bridge_action_t a) { return a==BR_PLAY||a==BR_AMP_UP||a==BR_AMP_DOWN||a==BR_SAVE||a==BR_REMOVE||a==BR_TRANSPORT; }
static bool text(const cJSON *object,const char *key,char *out,size_t cap,bool required) {
    const cJSON *value=cJSON_GetObjectItemCaseSensitive(object,key);
    if ((!value||cJSON_IsNull(value))&&!required) { out[0]=0; return true; }
    if(!cJSON_IsString(value)||!value->valuestring||strlen(value->valuestring)>=cap) return false;
    strcpy(out,value->valuestring); return true;
}
static bool number(const cJSON *object,const char *key,int *out,int low,int high) {
    const cJSON *v=cJSON_GetObjectItemCaseSensitive(object,key);
    if(!cJSON_IsNumber(v)||!isfinite(v->valuedouble)||v->valuedouble<low||v->valuedouble>high||floor(v->valuedouble)!=v->valuedouble) return false;
    *out=(int)v->valuedouble; return true;
}
static int saved(const cJSON *object,const char *key) {
    const cJSON *v=cJSON_GetObjectItemCaseSensitive(object,key);
    if(cJSON_IsTrue(v)) return 1;
    if(cJSON_IsFalse(v)) return 0;
    if(cJSON_IsString(v)) { if(!strcmp(v->valuestring,"saved")) return 1; if(!strcmp(v->valuestring,"unsaved")) return 0; }
    return -1;
}
static bool item(const cJSON *value,bridge_item_t *out) {
    out->saved=saved(value,"saved");
    return cJSON_IsObject(value)&&text(value,"reference",out->reference,sizeof(out->reference),true)&&
           text(value,"title",out->title,sizeof(out->title),true)&&
           text(value,"artist",out->artist,sizeof(out->artist),false)&&
           text(value,"album",out->album,sizeof(out->album),false)&&
           text(value,"kind",out->kind,sizeof(out->kind),false)&&
           text(value,"artist_reference",out->artist_reference,sizeof(out->artist_reference),false)&&
           text(value,"album_reference",out->album_reference,sizeof(out->album_reference),false)&&
           text(value,"artwork",out->artwork,sizeof(out->artwork),false);
}
bool bridge_encode(const bridge_request_t *r,char *json,size_t capacity) {
    if(r->action<BR_SNAPSHOT||r->action>BR_ARTWORK||!memchr(r->id,0,sizeof(r->id))||
       !memchr(r->kind,0,sizeof(r->kind))||!memchr(r->text,0,sizeof(r->text))||!memchr(r->cursor,0,sizeof(r->cursor))||!memchr(r->result_id,0,sizeof(r->result_id))||
       strlen(r->id)<16||strlen(r->id)>48||r->offset>10000||capacity>BRIDGE_REQUEST_MAX+1) return false;
    cJSON *root=cJSON_CreateObject(); if(!root) return false;
    cJSON_AddNumberToObject(root,"version",1); cJSON_AddStringToObject(root,"request_id",r->id);
    cJSON_AddStringToObject(root,"action",actions[r->action]); cJSON *args=cJSON_AddObjectToObject(root,"args");
    if(r->action==BR_SEARCH||r->action==BR_LIBRARY) {
        if(r->action==BR_SEARCH) cJSON_AddStringToObject(args,"query",r->text);
        cJSON_AddStringToObject(args,"kind",r->kind[0]?r->kind:"albums");
        cJSON_AddNumberToObject(args,"offset",r->offset);
        if(r->cursor[0]) cJSON_AddStringToObject(args,"cursor",r->cursor);
        if(r->result_id[0]) cJSON_AddStringToObject(args,"result_id",r->result_id);
    } else if(r->action==BR_AMP_UP||r->action==BR_AMP_DOWN) cJSON_AddStringToObject(args,"direction",r->action==BR_AMP_UP?"up":"down");
    else if(r->action==BR_QUEUE) cJSON_AddNumberToObject(args,"offset",r->offset);
    else if(r->action==BR_TRANSPORT) cJSON_AddStringToObject(args,"command",r->text);
    else if(r->action==BR_VOICE) cJSON_AddStringToObject(args,"fixture","silent");
    else if(r->action!=BR_SNAPSHOT) {
        cJSON_AddStringToObject(args,"reference",r->text);
        if(r->action==BR_BROWSE) cJSON_AddNumberToObject(args,"offset",r->offset);
        if(r->action==BR_SAVE||r->action==BR_REMOVE) cJSON_AddBoolToObject(args,"saved",r->action==BR_SAVE);
    }
    bool ok=cJSON_PrintPreallocated(root,json,(int)capacity,false); cJSON_Delete(root); return ok;
}
bool bridge_decode(const bridge_request_t *request,const char *json,size_t size,bridge_reply_t *r) {
    memset(r,0,sizeof(*r)); r->action=request->action; r->generation=request->generation;
    r->started_ms=request->started_ms; r->saved=-1; r->next_offset=-1;
    r->position_ms=r->duration_ms=r->bitrate=-1;
    r->outcome=bridge_mutation(request->action)?BR_UNKNOWN:BR_REJECTED;
    if(size>BRIDGE_RESPONSE_MAX||size==0) return false;
    const char *end=NULL;
    cJSON *root=cJSON_ParseWithLengthOpts(json,size,&end,false); if(!root) return false;
    while(end<json+size&&(*end==' '||*end=='\n'||*end=='\r'||*end=='\t')) end++;
    char id[65],outcome[24]; int version;
    bool ok=end==json+size&&number(root,"version",&version,1,1)&&
        text(root,"request_id",id,sizeof(id),true)&&!strcmp(id,request->id)&&
        text(root,"boot_id",r->boot_id,sizeof(r->boot_id),true)&&
        text(root,"outcome",outcome,sizeof(outcome),true)&&cJSON_IsBool(cJSON_GetObjectItemCaseSensitive(root,"fixture"));
    if(!ok) goto done;
    const cJSON *error=cJSON_GetObjectItemCaseSensitive(root,"error");
    if(error&&!cJSON_IsNull(error)&&!text(error,"code",r->error_code,sizeof(r->error_code),true)) { ok=false; goto done; }
    r->fixture=cJSON_IsTrue(cJSON_GetObjectItemCaseSensitive(root,"fixture"));
    if(!strcmp(outcome,"observed")) r->outcome=BR_OBSERVED;
    else if(!strcmp(outcome,"submitted")) r->outcome=BR_SUBMITTED;
    else if(!strcmp(outcome,"rejected")) r->outcome=BR_REJECTED;
    else if(!strcmp(outcome,"unknown")) r->outcome=BR_UNKNOWN;
    else { ok=false; goto done; }
    if((r->outcome==BR_OBSERVED&&bridge_mutation(request->action))||
       (r->outcome==BR_SUBMITTED&&!bridge_mutation(request->action))) { ok=false; goto done; }
    if(r->outcome!=BR_OBSERVED) goto done;
    const cJSON *data=cJSON_GetObjectItemCaseSensitive(root,"data");
    if(!cJSON_IsObject(data)) { ok=false; goto done; }
    const cJSON *list=cJSON_GetObjectItemCaseSensitive(data,request->action==BR_SNAPSHOT?"queue":"items");
    if((request->action==BR_SNAPSHOT||request->action==BR_SEARCH||request->action==BR_LIBRARY||request->action==BR_QUEUE)&&!list) { ok=false; goto done; }
    if(list) {
        if(!cJSON_IsArray(list)||cJSON_GetArraySize(list)>BRIDGE_PAGE_MAX) { ok=false; goto done; }
        const cJSON *value=NULL; cJSON_ArrayForEach(value,list) {
            if(!item(value,&r->items[r->count++])) { ok=false; goto done; }
        }
    }
    if(request->action==BR_SNAPSHOT) {
        int freshness;
        ok=number(data,"valid_for_ms",&freshness,0,5000)&&text(cJSON_GetObjectItemCaseSensitive(data,"player"),"title",r->title,sizeof(r->title),false);
        if(ok) r->valid_for_ms=(unsigned)freshness;
        const cJSON *player=cJSON_GetObjectItemCaseSensitive(data,"player");
        ok=ok&&text(player,"artist",r->artist,sizeof(r->artist),false)&&
            text(player,"album",r->album,sizeof(r->album),false)&&
            text(player,"sourceDetail",r->source,sizeof(r->source),false)&&
            text(player,"state",r->transport,sizeof(r->transport),false)&&
            text(data,"account",r->account,sizeof(r->account),false)&&
            text(player,"artwork",r->artwork,sizeof(r->artwork),false);
        const cJSON *current=cJSON_GetObjectItemCaseSensitive(data,"current_item");
        if(current&&!cJSON_IsNull(current)) ok=ok&&item(current,&r->item);
        number(player,"transportPosition",&r->position_ms,0,2147483647);
        number(player,"duration",&r->duration_ms,0,2147483647);
        number(player,"bitrate",&r->bitrate,1,2147483647);
    } else if(request->action==BR_BROWSE) {
        ok=item(cJSON_GetObjectItemCaseSensitive(data,"item"),&r->item);
        r->playable=cJSON_IsTrue(cJSON_GetObjectItemCaseSensitive(data,"playable"));
        const cJSON *next=cJSON_GetObjectItemCaseSensitive(data,"next_offset");
        if(next&&!cJSON_IsNull(next)) ok=ok&&number(data,"next_offset",&r->next_offset,0,10000);
    } else if(request->action==BR_SEARCH||request->action==BR_LIBRARY||request->action==BR_BROWSE||request->action==BR_QUEUE) {
        ok=text(data,"cursor",r->cursor,sizeof(r->cursor),false)&&text(data,"result_id",r->result_id,sizeof(r->result_id),false);
        const cJSON *next=cJSON_GetObjectItemCaseSensitive(data,"next_offset");
        if(next&&!cJSON_IsNull(next)) ok=ok&&number(data,"next_offset",&r->next_offset,0,10000);
    } else if(request->action==BR_VOICE) ok=text(data,"transcript",r->transcript,sizeof(r->transcript),true);
    else if(request->action==BR_ARTWORK) {
        const cJSON *available=cJSON_GetObjectItemCaseSensitive(data,"available");
        ok=cJSON_IsBool(available);
        r->artwork_available=cJSON_IsTrue(available);
        if(ok&&r->artwork_available) {
            int width,height,ttl; char format[24];
            const cJSON *pixels=cJSON_GetObjectItemCaseSensitive(data,"pixels");
            ok=number(data,"width",&width,BRIDGE_ART_SIDE,BRIDGE_ART_SIDE)&&
                number(data,"height",&height,BRIDGE_ART_SIDE,BRIDGE_ART_SIDE)&&
                number(data,"valid_for_ms",&ttl,1,60000)&&
                text(data,"format",format,sizeof(format),true)&&!strcmp(format,"rgb565be-hex")&&
                text(data,"reference",r->artwork,sizeof(r->artwork),true)&&!strcmp(r->artwork,request->text)&&
                cJSON_IsString(pixels)&&strlen(pixels->valuestring)==BRIDGE_ART_PIXELS*4;
            if(ok) {
                r->valid_for_ms=(unsigned)ttl;
                for(unsigned i=0;i<BRIDGE_ART_PIXELS*4;i++) {
                    char c=pixels->valuestring[i]; int nibble=c>='0'&&c<='9'?c-'0':c>='a'&&c<='f'?c-'a'+10:-1;
                    if(nibble<0) { ok=false; break; }
                    r->pixels[i/4]=(uint16_t)((r->pixels[i/4]<<4)|nibble);
                }
            }
        }
    }
    else if(request->action==BR_SAVED) r->saved=saved(data,"saved_state");
done:
    cJSON_Delete(root); r->valid=ok;
    if(!ok) r->outcome=bridge_mutation(request->action)?BR_UNKNOWN:BR_REJECTED;
    return ok;
}

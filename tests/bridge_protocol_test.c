#include "bridge_protocol.h"
#include <assert.h>
#include <string.h>
#include <stdio.h>
int main(void) {
    static bridge_request_t request;
    static bridge_reply_t reply;
    static char json[BRIDGE_REQUEST_MAX+1];
    strcpy(request.id,"0123456789abcdef0123456789abcdef"); request.action=BR_SEARCH;
    strcpy(request.text,"a \"quoted\" query"); assert(bridge_encode(&request,json,sizeof(json)));
    assert(strstr(json,"\\\"quoted\\\""));
    const char *valid="{\"version\":1,\"request_id\":\"0123456789abcdef0123456789abcdef\",\"boot_id\":\"boot\",\"fixture\":true,\"outcome\":\"observed\",\"data\":{\"items\":[{\"reference\":\"inputs/tidal/albums/1\",\"title\":\"Silent album\",\"saved\":\"unknown\"}],\"next_offset\":12,\"cursor\":null,\"result_id\":\"fixture\"}}";
    assert(bridge_decode(&request,valid,strlen(valid),&reply));
    assert(reply.count==1&&reply.items[0].saved==-1&&reply.next_offset==12&&reply.fixture);
    request.id[0]='x'; assert(!bridge_decode(&request,valid,strlen(valid),&reply)); request.id[0]='0';
    assert(!bridge_decode(&request,valid,BRIDGE_RESPONSE_MAX+1,&reply));
    request.action=BR_PLAY; assert(!bridge_decode(&request,valid,strlen(valid),&reply));
    assert(reply.outcome==BR_UNKNOWN);
    assert(!bridge_decode(&request,"{",1,&reply)); assert(reply.outcome==BR_UNKNOWN);
    request.action=BR_SEARCH; strcpy(request.kind,"artists");
    assert(bridge_encode(&request,json,sizeof(json))); assert(strstr(json,"\"kind\":\"artists\""));
    request.action=BR_LIBRARY; assert(bridge_encode(&request,json,sizeof(json))); assert(strstr(json,"library_page"));
    assert(!strstr(json,"query"));
    request.action=BR_TRANSPORT; strcpy(request.text,"pause");
    assert(bridge_mutation(request.action)&&bridge_encode(&request,json,sizeof(json))); assert(strstr(json,"\"command\":\"pause\""));
    assert(!bridge_decode(&request,"{",1,&reply)&&reply.outcome==BR_UNKNOWN);
    request.action=BR_SNAPSHOT;
    const char *snapshot="{\"version\":1,\"request_id\":\"0123456789abcdef0123456789abcdef\",\"boot_id\":\"boot\",\"fixture\":false,\"outcome\":\"observed\",\"data\":{\"queue\":[],\"valid_for_ms\":4000,\"player\":{\"title\":\"Real metadata\",\"duration\":null,\"bitrate\":null}}}";
    assert(bridge_decode(&request,snapshot,strlen(snapshot),&reply));
    assert(reply.bitrate==-1&&reply.duration_ms==-1&&reply.position_ms==-1&&!reply.item.reference[0]);
    static char art[BRIDGE_RESPONSE_MAX+1], hex[BRIDGE_ART_PIXELS*4+1];
    memset(hex,'f',sizeof(hex)-1); hex[sizeof(hex)-1]=0;
    request.action=BR_ARTWORK; strcpy(request.text,"/artwork/test.jpg");
    assert(bridge_encode(&request,json,sizeof(json))&&!bridge_mutation(request.action));
    int length=snprintf(art,sizeof(art),"{\"version\":1,\"request_id\":\"%s\",\"boot_id\":\"boot\",\"fixture\":true,\"outcome\":\"observed\",\"data\":{\"available\":true,\"reference\":\"%s\",\"width\":80,\"height\":80,\"format\":\"rgb565be-hex\",\"valid_for_ms\":60000,\"pixels\":\"%s\"}}",request.id,request.text,hex);
    assert(bridge_decode(&request,art,length,&reply)&&reply.artwork_available&&reply.pixels[6399]==65535);
    char *data=strstr(art,"\"pixels\":\"")+10; char original=*data; *data='z';
    assert(!bridge_decode(&request,art,length,&reply)); *data=original;
    char *width=strstr(art,"\"width\":80")+8; *width='9'; assert(!bridge_decode(&request,art,length,&reply)); *width='8';
    request.text[9]='x'; assert(!bridge_decode(&request,art,length,&reply));
    request.action=(bridge_action_t)-1; assert(!bridge_encode(&request,json,sizeof(json)));
    puts("PASS bounded protocol, identity, type and uncertain mutation checks"); return 0;
}

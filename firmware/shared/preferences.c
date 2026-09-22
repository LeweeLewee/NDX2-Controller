#include "preferences.h"
#include <string.h>
void preferences_defaults(preferences_t *p) { *p=(preferences_t){0,80,2}; }
bool preferences_valid(const preferences_t *p) {
    return p->palette<=2&&p->brightness>=30&&p->brightness<=100&&
        (p->timeout==0||p->timeout==1||p->timeout==2||p->timeout==5);
}
static uint32_t checksum(const uint8_t *data) {
    uint32_t crc=0xffffffff;
    for(unsigned i=0;i<8;i++) { crc^=data[i]; for(unsigned bit=0;bit<8;bit++) crc=(crc>>1)^((crc&1)?0xedb88320:0); }
    return ~crc;
}
bool preferences_encode(const preferences_t *p,uint8_t out[PREFERENCES_BYTES]) {
    if(!preferences_valid(p)) return false;
    memcpy(out,"NDPF",4); out[4]=1; out[5]=(uint8_t)p->palette; out[6]=(uint8_t)p->brightness; out[7]=(uint8_t)p->timeout;
    uint32_t crc=checksum(out); for(unsigned i=0;i<4;i++) out[8+i]=(uint8_t)(crc>>(i*8)); return true;
}
bool preferences_decode(const uint8_t *data,size_t size,preferences_t *p) {
    if(size!=PREFERENCES_BYTES||memcmp(data,"NDPF",4)||data[4]!=1) return false;
    uint32_t crc=0; for(unsigned i=0;i<4;i++) crc|=(uint32_t)data[8+i]<<(i*8);
    preferences_t candidate={data[5],data[6],data[7]};
    if(crc!=checksum(data)||!preferences_valid(&candidate)) return false;
    *p=candidate; return true;
}

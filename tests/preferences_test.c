#include "preferences_store.h"
#include <windows.h>
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void) {
    preferences_t defaults; preferences_defaults(&defaults);
    preferences_t chosen={2,65,5},loaded=defaults;
    uint8_t record[PREFERENCES_BYTES]; assert(preferences_encode(&chosen,record));
    assert(preferences_decode(record,sizeof(record),&loaded)&&loaded.palette==2&&loaded.brightness==65&&loaded.timeout==5);
    for(unsigned i=0;i<PREFERENCES_BYTES;i++) { record[i]^=1; assert(!preferences_decode(record,sizeof(record),&loaded)); record[i]^=1; }
    assert(!preferences_decode(record,11,&loaded));
    preferences_t invalid[]={ {3,80,2},{0,29,2},{0,101,2},{0,80,3} };
    for(unsigned i=0;i<4;i++) assert(!preferences_encode(&invalid[i],record));
    char dir[MAX_PATH],path[MAX_PATH],lock_path[MAX_PATH],temp[MAX_PATH];
    assert(GetTempPathA(sizeof(dir),dir)); assert(GetTempFileNameA(dir,"ndp",0,path)); DeleteFileA(path);
    snprintf(lock_path,sizeof(lock_path),"%s.lock",path); snprintf(temp,sizeof(temp),"%s.tmp.%lu",path,(unsigned long)GetCurrentProcessId());
    platform_t platform={0}; assert(desktop_preferences_init(&platform,path));
    assert(platform.load_preferences(&loaded)==PREF_DEFAULTS); assert(platform.save_preferences(&chosen));
    /* Readers never observe a partial replacement. A blocked replacement retains the old record. */
    HANDLE held=CreateFileA(path,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
    assert(held!=INVALID_HANDLE_VALUE); assert(!platform.save_preferences(&defaults)); CloseHandle(held);
    desktop_preferences_close(); assert(desktop_preferences_init(&platform,path));
    assert(platform.load_preferences(&loaded)==PREF_LOADED&&loaded.palette==2&&loaded.brightness==65&&loaded.timeout==5);
    /* A leftover temp cannot be truncated, and the last durable value remains intact. */
    FILE *file=fopen(temp,"wb"); assert(file); fputs("leftover",file); fclose(file);
    assert(!platform.save_preferences(&defaults)); DeleteFileA(temp);
    assert(platform.save_preferences(&defaults)); desktop_preferences_close();
    file=fopen(path,"wb"); assert(file); fputs("future or corrupt record",file); fclose(file);
    assert(desktop_preferences_init(&platform,path)); preferences_defaults(&loaded);
    assert(platform.load_preferences(&loaded)==PREF_UNAVAILABLE&&loaded.brightness==80);
    assert(!platform.save_preferences(&chosen)); /* Do not overwrite an unreadable/newer record. */
    desktop_preferences_close(); DeleteFileA(path);
    held=CreateFileA(lock_path,GENERIC_READ|GENERIC_WRITE,0,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
    assert(held!=INVALID_HANDLE_VALUE); assert(!desktop_preferences_init(&platform,path));
    assert(platform.load_preferences(&loaded)==PREF_UNAVAILABLE&&!platform.save_preferences(&chosen));
    CloseHandle(held); desktop_preferences_close(); DeleteFileA(lock_path);
    puts("PASS preference bounds, checksum, restart, failed replacement, leftovers and corruption preservation"); return 0;
}

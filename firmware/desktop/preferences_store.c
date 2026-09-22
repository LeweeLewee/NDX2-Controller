#include "preferences_store.h"
#include <windows.h>
#include <stdio.h>
#include <wchar.h>
static wchar_t location[1024],temporary[1080];
static HANDLE lock=INVALID_HANDLE_VALUE;
static bool writable;
static preferences_result_t load(preferences_t *p) {
    if(lock==INVALID_HANDLE_VALUE) return PREF_UNAVAILABLE;
    HANDLE file=CreateFileW(location,GENERIC_READ,FILE_SHARE_READ,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
    if(file==INVALID_HANDLE_VALUE) {
        if(GetLastError()==ERROR_FILE_NOT_FOUND) { writable=true; return PREF_DEFAULTS; }
        writable=false; return PREF_UNAVAILABLE;
    }
    uint8_t bytes[PREFERENCES_BYTES+1]; DWORD count=0;
    bool ok=ReadFile(file,bytes,sizeof(bytes),&count,NULL)&&preferences_decode(bytes,count,p);
    CloseHandle(file); writable=ok; return ok?PREF_LOADED:PREF_UNAVAILABLE;
}
static bool save(const preferences_t *p) {
    uint8_t bytes[PREFERENCES_BYTES];
    if(!writable||!preferences_encode(p,bytes)) return false;
    /* CREATE_NEW never truncates a leftover or another writer's temporary file. */
    HANDLE file=CreateFileW(temporary,GENERIC_WRITE,0,NULL,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,NULL);
    if(file==INVALID_HANDLE_VALUE) return false;
    DWORD count=0; bool ok=WriteFile(file,bytes,sizeof(bytes),&count,NULL)&&count==sizeof(bytes)&&FlushFileBuffers(file);
    if(!CloseHandle(file)) ok=false;
    if(ok) ok=MoveFileExW(temporary,location,MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH)!=0;
    if(!ok) DeleteFileW(temporary); /* this call owns the file it just created */
    return ok;
}
bool desktop_preferences_init(platform_t *platform,const char *path) {
    platform->load_preferences=load; platform->save_preferences=save;
    if(!MultiByteToWideChar(CP_UTF8,MB_ERR_INVALID_CHARS,path,-1,location,1024)) return false;
    wchar_t lock_path[1080]; swprintf(lock_path,1080,L"%ls.lock",location);
    swprintf(temporary,1080,L"%ls.tmp.%lu",location,(unsigned long)GetCurrentProcessId());
    lock=CreateFileW(lock_path,GENERIC_READ|GENERIC_WRITE,0,NULL,OPEN_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);
    return lock!=INVALID_HANDLE_VALUE;
}
void desktop_preferences_close(void) {
    if(lock!=INVALID_HANDLE_VALUE) CloseHandle(lock);
    lock=INVALID_HANDLE_VALUE; writable=false;
}

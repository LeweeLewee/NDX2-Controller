/* Desktop pipes carry bounded v1 JSON only; Python owns DPAPI and verified TLS.
 * The same bridge_encode/decode code is compiled into the ESP32 worker. */
#include "transport.h"
#include <SDL.h>
#include <windows.h>
#include <bcrypt.h>
#include <stdio.h>
#include <string.h>
static HANDLE input,output,child;
static char python_path[1024],pipe_command[2048];
static void stop_pipe(void) {
    if(input) { CloseHandle(input); input=NULL; }
    if(output) { CloseHandle(output); output=NULL; }
    if(child) {
        if(WaitForSingleObject(child,100)==WAIT_TIMEOUT) {
            TerminateProcess(child,0); WaitForSingleObject(child,INFINITE);
        }
        CloseHandle(child); child=NULL;
    }
}
static bool start_pipe(void) {
    SECURITY_ATTRIBUTES sa={sizeof(sa),NULL,TRUE}; HANDLE child_in=NULL,child_out=NULL;
    bool ok=false;
    if(!CreatePipe(&child_in,&input,&sa,0)||!CreatePipe(&output,&child_out,&sa,0)) goto done;
    if(!SetHandleInformation(input,HANDLE_FLAG_INHERIT,0)||!SetHandleInformation(output,HANDLE_FLAG_INHERIT,0)) goto done;
    STARTUPINFOA startup={0}; startup.cb=sizeof(startup); startup.dwFlags=STARTF_USESTDHANDLES;
    startup.hStdInput=child_in; startup.hStdOutput=child_out; startup.hStdError=GetStdHandle(STD_ERROR_HANDLE);
    PROCESS_INFORMATION process={0}; char command[sizeof(pipe_command)]; strcpy(command,pipe_command);
    if(!CreateProcessA(python_path,command,NULL,NULL,TRUE,CREATE_NO_WINDOW,NULL,NULL,&startup,&process)) goto done;
    child=process.hProcess; CloseHandle(process.hThread); ok=true;
done:
    if(child_in) CloseHandle(child_in);
    if(child_out) CloseHandle(child_out);
    if(!ok) stop_pipe();
    return ok;
}
static SDL_mutex *mutex;
static SDL_cond *condition;
static SDL_Thread *thread;
static SDL_atomic_t generation;
static bool running,occupied,ready,queued;
static bridge_request_t job;
static bridge_reply_t result;
static char encoded[BRIDGE_REQUEST_MAX+2],received[BRIDGE_RESPONSE_MAX+1];
static bool exchange(const bridge_request_t *r,bridge_reply_t *reply) {
    if(!bridge_encode(r,encoded,BRIDGE_REQUEST_MAX+1)) return false;
    size_t length=strlen(encoded); encoded[length++]='\n';
    DWORD written;
    if(!WriteFile(input,encoded,(DWORD)length,&written,NULL)||written!=length) return false;
    size_t total=0; uint64_t deadline=SDL_GetTicks64()+6500;
    while(SDL_GetTicks64()<deadline) {
        DWORD available=0,count=0;
        if(!PeekNamedPipe(output,NULL,0,NULL,&available,NULL)) return false;
        if(!available) { SDL_Delay(5); continue; }
        if(total>=BRIDGE_RESPONSE_MAX) return false;
        if(!ReadFile(output,received+total,1,&count,NULL)||count!=1) return false;
        if(received[total]=='\n') return bridge_decode(r,received,total,reply);
        total++;
    }
    return false;
}
static int worker(void *unused) {
    (void)unused;
    for(;;) {
        SDL_LockMutex(mutex);
        while(running&&!queued) SDL_CondWait(condition,mutex);
        if(!running) { SDL_UnlockMutex(mutex); return 0; }
        queued=false; SDL_UnlockMutex(mutex);
        memset(&result,0,sizeof(result)); result.action=job.action; result.generation=job.generation;
        result.started_ms=job.started_ms; result.outcome=bridge_mutation(job.action)?BR_UNKNOWN:BR_REJECTED;
        if(job.generation==(uint32_t)SDL_AtomicGet(&generation)) {
            if((!child&&!start_pipe())||!exchange(&job,&result)) {
                result.valid=false;
                /* Discard the failed stream, including any late reply. A later
                 * request may start a helper; this job is never retried. */
                stop_pipe();
            }
        }
        SDL_LockMutex(mutex); ready=true; SDL_UnlockMutex(mutex);
    }
}
static bool submit(const bridge_request_t *request) {
    SDL_LockMutex(mutex);
    bool accepted=!occupied&&running;
    if(accepted) { job=*request; occupied=true; queued=true; SDL_CondSignal(condition); }
    SDL_UnlockMutex(mutex); return accepted;
}
static bool poll(bridge_reply_t *reply) {
    SDL_LockMutex(mutex); bool available=ready;
    if(available) { *reply=result; ready=false; occupied=false; }
    SDL_UnlockMutex(mutex); return available;
}
static void invalidate(uint32_t value) { SDL_AtomicSet(&generation,(int)value); }
static void request_id(char out[49]) {
    unsigned char bytes[24];
    if(BCryptGenRandom(NULL,bytes,sizeof(bytes),BCRYPT_USE_SYSTEM_PREFERRED_RNG)!=0) { out[0]=0; return; }
    for(unsigned i=0;i<24;i++) snprintf(out+i*2,3,"%02x",bytes[i]);
}
bool desktop_transport_init(platform_t *platform,const char *python,const char *config) {
    if(strchr(python,'"')||strchr(config,'"')) return false;
    if(strlen(python)>=sizeof(python_path)||
       snprintf(pipe_command,sizeof(pipe_command),"\"%s\" tools/m2_pipe.py \"%s\"",python,config)>=(int)sizeof(pipe_command)) return false;
    strcpy(python_path,python);
    mutex=SDL_CreateMutex(); condition=SDL_CreateCond();
    if(!mutex||!condition) goto failed;
    running=true; occupied=ready=queued=false; SDL_AtomicSet(&generation,0);
    thread=SDL_CreateThread(worker,"bridge",NULL);
    if(!thread) goto failed;
    platform->submit=submit; platform->poll=poll; platform->invalidate=invalidate; platform->request_id=request_id;
    return true;
failed:
    running=false;
    if(condition) SDL_DestroyCond(condition);
    if(mutex) SDL_DestroyMutex(mutex);
    condition=NULL; mutex=NULL;
    return false;
}
void desktop_transport_close(void) {
    if(!thread) return;
    SDL_LockMutex(mutex); running=false; SDL_CondSignal(condition); SDL_UnlockMutex(mutex);
    SDL_WaitThread(thread,NULL); thread=NULL; stop_pipe();
    SDL_DestroyCond(condition); SDL_DestroyMutex(mutex); condition=NULL; mutex=NULL;
}

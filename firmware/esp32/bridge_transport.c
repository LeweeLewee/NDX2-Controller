#include "bridge_transport.h"
#include "esp_http_client.h"
#include "esp_timer.h"
#include "esp_random.h"
#include "esp_flash_encrypt.h"
#include "esp_secure_boot.h"
#include "esp_wifi.h"
#include "esp_netif.h"
#include "esp_netif_sntp.h"
#include "esp_event.h"
#include "nvs_flash.h"
#include "nvs.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/task.h"
#include <stdatomic.h>
#include <stdio.h>
#include <string.h>
static QueueHandle_t requests,replies;
static atomic_uint current_generation;
static char url[257],credential[129],trust[8192],ntp[128];
static char encoded[BRIDGE_REQUEST_MAX+1],received[BRIDGE_RESPONSE_MAX+1];
static bridge_request_t job;
static bridge_reply_t result;
static void network_event(void *arg,esp_event_base_t base,int32_t id,void *data) {
    (void)arg;(void)data;
    if(base==WIFI_EVENT&&(id==WIFI_EVENT_STA_START||id==WIFI_EVENT_STA_DISCONNECTED)) esp_wifi_connect();
}
static bool exchange(void) {
    if(!bridge_encode(&job,encoded,sizeof(encoded))) return false;
    esp_http_client_config_t config={.url=url,.cert_pem=trust,.timeout_ms=5000,
        .disable_auto_redirect=true,.keep_alive_enable=false,.buffer_size=1024};
    esp_http_client_handle_t http=esp_http_client_init(&config); if(!http) return false;
    char authorization[140]; snprintf(authorization,sizeof(authorization),"Bearer %s",credential);
    esp_http_client_set_method(http,HTTP_METHOD_POST);
    esp_http_client_set_header(http,"Authorization",authorization);
    esp_http_client_set_header(http,"Content-Type","application/json");
    bool ok=false; int length=(int)strlen(encoded);
    if(esp_http_client_open(http,length)!=ESP_OK) goto done;
    if(esp_http_client_write(http,encoded,length)!=length) goto done;
    int64_t announced=esp_http_client_fetch_headers(http);
    if(esp_http_client_get_status_code(http)!=200||announced>BRIDGE_RESPONSE_MAX) goto done;
    int total=0; int64_t deadline=esp_timer_get_time()+7000000;
    while(total<=BRIDGE_RESPONSE_MAX) {
        if(esp_timer_get_time()>deadline) goto done;
        int n=esp_http_client_read(http,received+total,BRIDGE_RESPONSE_MAX+1-total);
        if(n<0) goto done;
        if(n==0) break;
        total+=n;
    }
    if(total>BRIDGE_RESPONSE_MAX||!esp_http_client_is_complete_data_received(http)) goto done;
    ok=bridge_decode(&job,received,(size_t)total,&result);
done:
    esp_http_client_close(http); esp_http_client_cleanup(http); return ok;
}
static void worker(void *unused) {
    (void)unused;
    for(;;) if(xQueueReceive(requests,&job,portMAX_DELAY)==pdTRUE) {
        memset(&result,0,sizeof(result)); result.action=job.action; result.generation=job.generation;
        result.started_ms=job.started_ms; result.outcome=bridge_mutation(job.action)?BR_UNKNOWN:BR_REJECTED;
        if(job.generation==atomic_load(&current_generation)) result.valid=exchange();
        /* No retries, including on TLS failure or uncertain writes. */
        xQueueSend(replies,&result,portMAX_DELAY);
    }
}
static bool submit(const bridge_request_t *request) { return xQueueSend(requests,request,0)==pdTRUE; }
static bool poll_reply(bridge_reply_t *reply) { return xQueueReceive(replies,reply,0)==pdTRUE; }
static void invalidate(uint32_t generation) { atomic_store(&current_generation,generation); xQueueReset(requests); }
static void request_id(char out[49]) {
    unsigned char bytes[24]; esp_fill_random(bytes,sizeof(bytes));
    for(unsigned i=0;i<24;i++) snprintf(out+i*2,3,"%02x",bytes[i]);
}
static bool read_key(nvs_handle_t handle,const char *key,char *out,size_t capacity) {
    return nvs_get_str(handle,key,out,&capacity)==ESP_OK&&out[0];
}
bool esp_bridge_start(platform_t *platform) {
#ifndef CONFIG_NVS_ENCRYPTION
    #define CONFIG_NVS_ENCRYPTION 0
#endif
    /* No provider secrets, no insecure fallback and no efuse writes here. */
    if(!CONFIG_NVS_ENCRYPTION||!esp_flash_encryption_enabled()||!esp_secure_boot_enabled()) return false;
    if(nvs_flash_init()!=ESP_OK) return false;
    nvs_handle_t handle; if(nvs_open("controller",NVS_READONLY,&handle)!=ESP_OK) return false;
    wifi_config_t wifi={0};
    bool loaded=read_key(handle,"url",url,sizeof(url))&&read_key(handle,"credential",credential,sizeof(credential))&&
        read_key(handle,"trust",trust,sizeof(trust))&&read_key(handle,"ntp",ntp,sizeof(ntp))&&
        read_key(handle,"ssid",(char *)wifi.sta.ssid,sizeof(wifi.sta.ssid))&&
        read_key(handle,"password",(char *)wifi.sta.password,sizeof(wifi.sta.password));
    nvs_close(handle);
    if(!loaded||strncmp(url,"https://",8)||strchr(credential,'\r')||strchr(credential,'\n')) return false;
    size_t url_length=strlen(url);
    if(url_length<20||strcmp(url+url_length-11,"/v1/request")||strpbrk(url,"@?#")) return false;
    if(esp_netif_init()!=ESP_OK||esp_event_loop_create_default()!=ESP_OK) return false;
    esp_netif_create_default_wifi_sta();
    wifi_init_config_t init=WIFI_INIT_CONFIG_DEFAULT();
    if(esp_wifi_init(&init)!=ESP_OK) return false;
    esp_event_handler_register(WIFI_EVENT,ESP_EVENT_ANY_ID,network_event,NULL);
    esp_wifi_set_storage(WIFI_STORAGE_RAM); esp_wifi_set_mode(WIFI_MODE_STA); esp_wifi_set_config(WIFI_IF_STA,&wifi);
    if(esp_wifi_start()!=ESP_OK) return false;
    esp_sntp_config_t time_config=ESP_NETIF_SNTP_DEFAULT_CONFIG(ntp); esp_netif_sntp_init(&time_config);
    requests=xQueueCreate(1,sizeof(bridge_request_t)); replies=xQueueCreate(1,sizeof(bridge_reply_t));
    if(!requests||!replies||xTaskCreate(worker,"bridge",8192,NULL,3,NULL)!=pdPASS) return false;
    platform->submit=submit; platform->poll=poll_reply; platform->invalidate=invalidate; platform->request_id=request_id;
    return true;
}

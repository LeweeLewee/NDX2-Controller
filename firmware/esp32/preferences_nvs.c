#include "preferences_nvs.h"
#include "nvs.h"
#include "nvs_flash.h"
static bool writable;
static preferences_result_t load(preferences_t *p) {
    writable=false;
    /* Never erase/reinitialize a full, damaged or newer-version partition. */
    if(nvs_flash_init()!=ESP_OK) return PREF_UNAVAILABLE;
    nvs_handle_t handle; esp_err_t error=nvs_open("display_prefs",NVS_READONLY,&handle);
    if(error==ESP_ERR_NVS_NOT_FOUND) { writable=true; return PREF_DEFAULTS; }
    if(error!=ESP_OK) return PREF_UNAVAILABLE;
    uint8_t bytes[PREFERENCES_BYTES]; size_t size=sizeof(bytes);
    error=nvs_get_blob(handle,"record",bytes,&size); nvs_close(handle);
    if(error==ESP_ERR_NVS_NOT_FOUND) { writable=true; return PREF_DEFAULTS; }
    if(error!=ESP_OK||!preferences_decode(bytes,size,p)) return PREF_UNAVAILABLE;
    writable=true; return PREF_LOADED;
}
static bool save(const preferences_t *p) {
    uint8_t bytes[PREFERENCES_BYTES];
    if(!writable||!preferences_encode(p,bytes)) return false;
    nvs_handle_t handle; if(nvs_open("display_prefs",NVS_READWRITE,&handle)!=ESP_OK) return false;
    esp_err_t error=nvs_set_blob(handle,"record",bytes,sizeof(bytes));
    if(error==ESP_OK) error=nvs_commit(handle);
    nvs_close(handle); return error==ESP_OK;
}
void esp_preferences_init(platform_t *platform) { platform->load_preferences=load; platform->save_preferences=save; }

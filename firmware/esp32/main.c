/* Vendor RGB/touch driver stays in the generated, checksum-pinned project. */
#include "waveshare_rgb_lcd_port.h"
#include "esp_timer.h"
#include "esp_system.h"
#include "ui.h"
#include "fixture.h"
#include "preferences_nvs.h"
#include "bridge_transport.h"
static uint64_t now_ms(void) { return esp_timer_get_time()/1000; }
static void diagnostic(const char *event) {
    ESP_LOGI("HP01", "ms=%llu event=%s free_heap=%lu min_heap=%lu fixture=1",
        (unsigned long long)now_ms(),event,(unsigned long)esp_get_free_heap_size(),
        (unsigned long)esp_get_minimum_free_heap_size());
}
void app_main(void) {
    diagnostic("boot_no_sleep_no_microphone");
    ESP_ERROR_CHECK(waveshare_esp32_s3_rgb_lcd_init());
    static platform_t platform;
    platform=fixture_platform(now_ms,diagnostic);
    diagnostic(esp_bridge_start(&platform)?"protected_bridge_client":"silent_fixture_no_provisioning");
    esp_preferences_init(&platform);
    if (lvgl_port_lock(-1)) {
        controller_ui_init(&platform);
        lvgl_port_unlock();
    }
}

#pragma once
#include "controller.h"
/* Returns false unless secure boot/flash/NVS protection and provisioned keys exist. */
bool esp_bridge_start(platform_t *platform);

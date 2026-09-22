#pragma once
#include "controller.h"
void controller_ui_init(platform_t *platform);
/* Call on every physical contact sample, including release, before LVGL input. */
bool controller_ui_touch(bool pressed);
void controller_ui_disconnect(void);
/* Read-only diagnostics for native smoke tests and HP-01 tooling. */
const controller_t *controller_ui_state(void);
bool controller_ui_ready(void);

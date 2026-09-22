#pragma once
#include "controller.h"
/* Path is UTF-8. Caller creates the parent. Close releases the per-file lock. */
bool desktop_preferences_init(platform_t *platform,const char *path);
void desktop_preferences_close(void);

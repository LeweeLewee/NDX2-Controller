#pragma once
#include "controller.h"
platform_t fixture_platform(uint64_t (*now)(void), void (*log)(const char *));

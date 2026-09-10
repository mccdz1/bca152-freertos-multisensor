#pragma once

#include <stdint.h>
#include <stdbool.h>
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "freertos/semphr.h"
#include "freertos/event_groups.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Event Group Bits */
#define EVENT_ACTIVE (1 << 0)
#define EVENT_MOTION (1 << 1)
#define EVENT_ALARM  (1 << 2)

/* Shared FreeRTOS IPC handles */
extern QueueHandle_t sensorQueue;
extern SemaphoreHandle_t serialMutex;
extern EventGroupHandle_t systemEventGroup;

/**
 * @brief Initialize all FreeRTOS synchronization and IPC objects
 */
void rtos_objects_init(void);

/**
 * @brief Thread-safe serial logging protected by serialMutex
 */
void safe_log(const char *tag, const char *format, ...);

#ifdef __cplusplus
}
#endif

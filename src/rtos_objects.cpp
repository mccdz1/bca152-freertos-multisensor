#include "rtos_objects.h"
#include <stdio.h>
#include <stdarg.h>
#include "esp_log.h"

QueueHandle_t sensorQueue = nullptr;
SemaphoreHandle_t serialMutex = nullptr;
EventGroupHandle_t systemEventGroup = nullptr;

void rtos_objects_init(void)
{
    /* Sized to hold 5 SensorData records */
    sensorQueue = xQueueCreate(5, 16); // sizeof(SensorData) = 16 bytes

    /* Mutex protecting shared serial/log terminal */
    serialMutex = xSemaphoreCreateMutex();

    /* Event group signaling system events (ACTIVE, MOTION, ALARM) */
    systemEventGroup = xEventGroupCreate();

    if (systemEventGroup != nullptr) {
        /* Default initial state: ACTIVE */
        xEventGroupSetBits(systemEventGroup, EVENT_ACTIVE);
    }
}

void safe_log(const char *tag, const char *format, ...)
{
    char buffer[256];
    va_list args;
    va_start(args, format);
    vsnprintf(buffer, sizeof(buffer), format, args);
    va_end(args);

    if (serialMutex != nullptr) {
        if (xSemaphoreTake(serialMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            printf("[%s] %s\n", tag, buffer);
            xSemaphoreGive(serialMutex);
            return;
        }
    }
    printf("[%s] %s\n", tag, buffer);
}

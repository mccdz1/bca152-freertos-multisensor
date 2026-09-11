#include "motion.h"
#include "rtos_objects.h"
#include "system_state.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

void motion_init(void)
{
    gpio_config_t io_conf = {};
    io_conf.intr_type = GPIO_INTR_DISABLE;
    io_conf.mode = GPIO_MODE_INPUT;
    io_conf.pin_bit_mask = (1ULL << PIN_PIR);
    io_conf.pull_down_en = GPIO_PULLDOWN_ENABLE;
    io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
    gpio_config(&io_conf);
}

bool motion_read_current(void)
{
    return gpio_get_level(PIN_PIR) == 1;
}

void motion_task(void *pvParameters)
{
    bool last_state = false;

    for (;;) {
        bool current = motion_read_current();

        if (current && !last_state) {
            /* Rising edge: Motion detected */
            if (systemEventGroup != nullptr) {
                xEventGroupSetBits(systemEventGroup, EVENT_MOTION);
            }
            system_state_record_motion();
            safe_log("MOTION", "PIR Motion Triggered! (EVENT_MOTION signaled)");
        } else if (!current && last_state) {
            /* Falling edge: Motion cleared */
            if (systemEventGroup != nullptr) {
                xEventGroupClearBits(systemEventGroup, EVENT_MOTION);
            }
        }

        last_state = current;
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

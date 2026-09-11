#include "alarm.h"
#include "rtos_objects.h"
#include "sensors.h"
#include "system_state.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

AlarmState evaluateTemperature(float temperature)
{
    if (temperature < LOW_TEMPERATURE_LIMIT) {
        return AlarmState::LOW_TEMPERATURE;
    } else if (temperature > HIGH_TEMPERATURE_LIMIT) {
        return AlarmState::HIGH_TEMPERATURE;
    }
    return AlarmState::NORMAL;
}

void alarm_init(void)
{
    gpio_config_t io_conf = {};
    io_conf.intr_type = GPIO_INTR_DISABLE;
    io_conf.mode = GPIO_MODE_OUTPUT;
    io_conf.pin_bit_mask = (1ULL << PIN_BUZZER);
    io_conf.pull_down_en = GPIO_PULLDOWN_ENABLE;
    io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
    gpio_config(&io_conf);

    gpio_set_level(PIN_BUZZER, 0);
}

void buzzer_set(bool state)
{
    gpio_set_level(PIN_BUZZER, state ? 1 : 0);
}

void alarm_task(void *pvParameters)
{
    SensorData reading;

    for (;;) {
        /* Block waiting for sensor update on queue */
        if (xQueueReceive(sensorQueue, &reading, portMAX_DELAY) == pdTRUE) {
            AlarmState state = evaluateTemperature(reading.temperature);

            if (state != AlarmState::NORMAL) {
                /* Temperature outside normal bounds [18..30 C] -> Alarm Active */
                buzzer_set(true);
                if (systemEventGroup != nullptr) {
                    xEventGroupSetBits(systemEventGroup, EVENT_ALARM);
                }
                safe_log("ALARM", "ALARM TRIGGERED! Temp=%.2f C (Threshold: 18-30 C)", reading.temperature);
            } else {
                /* Normal temperature -> Alarm Inactive */
                buzzer_set(false);
                if (systemEventGroup != nullptr) {
                    xEventGroupClearBits(systemEventGroup, EVENT_ALARM);
                }
            }
        }
    }
}

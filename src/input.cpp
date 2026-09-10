#include "input.h"
#include "rtos_objects.h"
#include "system_state.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static DisplayMode current_mode = DisplayMode::TEMPERATURE;

DisplayMode nextDisplayMode(DisplayMode current)
{
    switch (current) {
        case DisplayMode::TEMPERATURE:
            return DisplayMode::HUMIDITY;
        case DisplayMode::HUMIDITY:
            return DisplayMode::LIGHT;
        case DisplayMode::LIGHT:
            return DisplayMode::MOTION;
        case DisplayMode::MOTION:
            return DisplayMode::TEMPERATURE;
        default:
            return DisplayMode::TEMPERATURE;
    }
}

DisplayMode previousDisplayMode(DisplayMode current)
{
    switch (current) {
        case DisplayMode::TEMPERATURE:
            return DisplayMode::MOTION;
        case DisplayMode::HUMIDITY:
            return DisplayMode::TEMPERATURE;
        case DisplayMode::LIGHT:
            return DisplayMode::HUMIDITY;
        case DisplayMode::MOTION:
            return DisplayMode::LIGHT;
        default:
            return DisplayMode::TEMPERATURE;
    }
}

void input_init(void)
{
    gpio_config_t io_conf = {};
    io_conf.intr_type = GPIO_INTR_DISABLE;
    io_conf.mode = GPIO_MODE_INPUT;
    io_conf.pin_bit_mask = (1ULL << PIN_ENCODER_CLK) |
                           (1ULL << PIN_ENCODER_DT) |
                           (1ULL << PIN_ENCODER_SW);
    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    io_conf.pull_up_en = GPIO_PULLUP_ENABLE;
    gpio_config(&io_conf);
}

DisplayMode input_get_display_mode(void)
{
    return current_mode;
}

static const char* display_mode_to_string(DisplayMode mode)
{
    switch (mode) {
        case DisplayMode::TEMPERATURE: return "TEMPERATURE";
        case DisplayMode::HUMIDITY:    return "HUMIDITY";
        case DisplayMode::LIGHT:       return "LIGHT";
        case DisplayMode::MOTION:      return "MOTION";
        default:                       return "UNKNOWN";
    }
}

void input_task(void *pvParameters)
{
    int last_clk = gpio_get_level(PIN_ENCODER_CLK);

    for (;;) {
        int current_clk = gpio_get_level(PIN_ENCODER_CLK);

        /* Detect transition on CLK line (falling edge) */
        if (last_clk == 1 && current_clk == 0) {
            int dt_level = gpio_get_level(PIN_ENCODER_DT);

            if (dt_level != current_clk) {
                /* Clockwise rotation */
                current_mode = nextDisplayMode(current_mode);
                safe_log("INPUT", "Encoder rotated CW -> Mode: %s", display_mode_to_string(current_mode));
            } else {
                /* Counter-clockwise rotation */
                current_mode = previousDisplayMode(current_mode);
                safe_log("INPUT", "Encoder rotated CCW -> Mode: %s", display_mode_to_string(current_mode));
            }

            /* User interaction also wakes up/maintains system state */
            system_state_record_motion();
        }

        last_clk = current_clk;
        vTaskDelay(pdMS_TO_TICKS(10)); // 10ms sampling/debounce
    }
}

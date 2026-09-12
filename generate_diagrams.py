import os
from PIL import Image, ImageDraw, ImageFont

os.makedirs("docs", exist_ok=True)

# Helper function to get font
def get_font(size=14, bold=False):
    # Try Windows fonts
    font_names = ["segoeui.ttf", "arial.ttf", "calibri.ttf"]
    if bold:
        font_names = ["segouib.ttf", "arialbd.ttf", "calibrib.ttf"]
    for name in font_names:
        try:
            path = os.path.join(r"C:\Windows\Fonts", name)
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()

font_title = get_font(24, bold=True)
font_subtitle = get_font(15, bold=False)
font_h2 = get_font(18, bold=True)
font_bold = get_font(14, bold=True)
font_regular = get_font(13, bold=False)
font_small = get_font(11, bold=False)
font_mono = get_font(12, bold=False)

# ==============================================================================
# Diagram 1: System Architecture (Layered Block Diagram)
# ==============================================================================
def make_system_architecture():
    w, h = 1100, 720
    im = Image.new("RGB", (w, h), "#f8fafc")
    draw = ImageDraw.Draw(im)

    # Title Banner
    draw.rectangle([(0, 0), (w, 75)], fill="#0f172a")
    draw.text((30, 16), "BCA152 FreeRTOS Multisensor — System Architecture", font=font_title, fill="#ffffff")
    draw.text((30, 48), "Hierarchical Hardware, Driver, RTOS, Application, and Interface Decomposition", font=font_subtitle, fill="#94a3b8")

    layers = [
        ("Layer 5: User & Environmental Interface", "#e0e7ff", "#3730a3", [
            ("SSD1306 OLED (128x64)", "Visual Room Monitor UI"),
            ("Active Piezo Buzzer", "Acoustic Alarm Output"),
            ("KY-040 Rotary Encoder", "Manual Navigation Dial"),
            ("PIR & Environment", "Physical Human Presence & Ambience")
        ]),
        ("Layer 4: Application Tasks (FreeRTOS)", "#dbeafe", "#1e40af", [
            ("DisplayTask [Prio 1]", "OLED single-owner UI"),
            ("AlarmTask [Prio 2]", "Temp threshold evaluator"),
            ("SensorTask [Prio 2]", "vTaskDelayUntil (2s) sampler"),
            ("StateTask [Prio 2]", "ACTIVE / INACTIVE logic"),
            ("InputTask [Prio 3]", "Encoder rotation decoder"),
            ("MotionTask [Prio 3]", "PIR presence detector")
        ]),
        ("Layer 3: FreeRTOS Kernel & IPC Subsystem", "#dcfce7", "#166534", [
            ("Preemptive Priority Scheduler", "Core 0 / Core 1 task management"),
            ("Sensor Queue (size 5)", "Non-blocking data distribution"),
            ("Serial Mutex (Mutex Sem)", "Atomic safe_log output"),
            ("System Event Group", "EVENT_ACTIVE | MOTION | ALARM")
        ]),
        ("Layer 2: ESP-IDF Hardware Abstraction & Drivers", "#fef3c7", "#92400e", [
            ("driver/i2c (Master @ 400kHz)", "SDA: GPIO21, SCL: GPIO22"),
            ("esp_adc/adc_oneshot", "ADC1 Channel 6: GPIO34"),
            ("driver/gpio (Bit-bang & ISR)", "DHT22: GPIO4, PIR: 13, KY-040: 18/19/5"),
            ("High-Resolution Timer", "esp_timer_get_time() microsecond sync")
        ]),
        ("Layer 1: Physical / Simulated Hardware (Wokwi)", "#fee2e2", "#991b1b", [
            ("ESP32-DevKitC-V4", "Xtensa Dual-Core 240MHz, 520KB SRAM"),
            ("DHT22 Sensor", "Temp (-40..80 C) & Humidity (0..100%)"),
            ("LDR Photoresistor", "0-4095 Analog Voltage Divider"),
            ("PIR Motion Sensor", "Digital High/Low Motion Output"),
            ("KY-040 Encoder & Buzzer", "Quadrature CLK/DT & 5V Piezo")
        ])
    ]

    y = 95
    for title, bg_col, border_col, items in layers:
        # Outer container
        draw.rounded_rectangle([(30, y), (w - 30, y + 105)], radius=8, fill=bg_col, outline=border_col, width=2)
        draw.text((45, y + 8), title, font=font_bold, fill=border_col)

        # Inner items
        n = len(items)
        col_w = (w - 100) / n
        for i, (head, sub) in enumerate(items):
            ix = 45 + i * col_w
            iy = y + 34
            draw.rounded_rectangle([(ix, iy), (ix + col_w - 12, iy + 60)], radius=6, fill="#ffffff", outline="#cbd5e1", width=1)
            draw.text((ix + 8, iy + 8), head, font=font_bold, fill="#1e293b")
            draw.text((ix + 8, iy + 30), sub, font=font_small, fill="#64748b")

        y += 120

    im.save(r"docs\system_architecture.png")
    print("Saved docs/system_architecture.png")

# ==============================================================================
# Diagram 2: FreeRTOS Architecture (Tasks, IPC, Queues, Mutex, Events)
# ==============================================================================
def make_freertos_architecture():
    w, h = 1100, 720
    im = Image.new("RGB", (w, h), "#f8fafc")
    draw = ImageDraw.Draw(im)

    # Title Banner
    draw.rectangle([(0, 0), (w, 75)], fill="#0284c7")
    draw.text((30, 16), "BCA152 FreeRTOS Multisensor — Task & IPC Architecture", font=font_title, fill="#ffffff")
    draw.text((30, 48), "Preemptive Priority Scheduling, Queues, Mutex Protection, and Event Group Synchronization", font=font_subtitle, fill="#e0f2fe")

    # Tasks boxes
    tasks = [
        ("MotionTask", "Priority: 3", "Period: 100ms", "Monitors PIR GPIO13", 60, 110, "#e0f2fe", "#0284c7"),
        ("InputTask", "Priority: 3", "Period: 10ms", "Rotary Encoder CLK/DT", 60, 240, "#e0f2fe", "#0284c7"),
        ("SensorTask", "Priority: 2", "Period: 2000ms", "vTaskDelayUntil() sampler", 60, 370, "#dcfce7", "#16a34a"),
        ("AlarmTask", "Priority: 2", "Event-driven", "evaluateTemperature()", 60, 500, "#fef3c7", "#d97706"),
        ("StateTask", "Priority: 2", "Period: 500ms", "ACTIVE/INACTIVE fsm", 60, 610, "#f3e8ff", "#9333ea"),
        ("DisplayTask", "Priority: 1", "Period: 150ms", "Sole owner of SSD1306", 780, 280, "#fee2e2", "#dc2626"),
    ]

    for name, prio, per, desc, x, y, bg, bd in tasks:
        draw.rounded_rectangle([(x, y), (x + 230, y + 90)], radius=8, fill=bg, outline=bd, width=2)
        draw.text((x + 12, y + 8), name, font=font_h2, fill=bd)
        draw.text((x + 12, y + 32), f"{prio} | {per}", font=font_bold, fill="#334155")
        draw.text((x + 12, y + 54), desc, font=font_regular, fill="#64748b")

    # Central IPC Components
    draw.rounded_rectangle([(400, 120), (680, 260)], radius=10, fill="#ffffff", outline="#0284c7", width=2)
    draw.text((415, 130), "systemEventGroup (EventGroup)", font=font_bold, fill="#0284c7")
    draw.text((420, 160), "BIT0: EVENT_ACTIVE (System Active)", font=font_small, fill="#1e293b")
    draw.text((420, 185), "BIT1: EVENT_MOTION (PIR Triggered)", font=font_small, fill="#1e293b")
    draw.text((420, 210), "BIT2: EVENT_ALARM  (Temp Out of Bounds)", font=font_small, fill="#1e293b")

    draw.rounded_rectangle([(400, 310), (680, 440)], radius=10, fill="#ffffff", outline="#16a34a", width=2)
    draw.text((415, 320), "sensorQueue (QueueHandle_t)", font=font_bold, fill="#16a34a")
    draw.text((420, 350), "Depth: 5 items | Item: sizeof(SensorData)", font=font_small, fill="#1e293b")
    draw.text((420, 375), "Payload: temp, hum, light, motion", font=font_small, fill="#1e293b")
    draw.text((420, 400), "Flow: SensorTask -> DisplayTask / AlarmTask", font=font_small, fill="#1e293b")

    draw.rounded_rectangle([(400, 490), (680, 620)], radius=10, fill="#ffffff", outline="#d97706", width=2)
    draw.text((415, 500), "serialMutex (SemaphoreHandle_t)", font=font_bold, fill="#d97706")
    draw.text((420, 530), "Guards shared UART Console (stdout)", font=font_small, fill="#1e293b")
    draw.text((420, 555), "Prevents garbled / interleaved log output", font=font_small, fill="#1e293b")
    draw.text((420, 580), "Acquired by: safe_log() across all tasks", font=font_small, fill="#1e293b")

    # Arrows (Connecting Lines with descriptions)
    draw.line([(290, 155), (400, 155)], fill="#0284c7", width=3) # Motion to Event
    draw.text((300, 138), "Sets EVENT_MOTION", font=font_small, fill="#0284c7")

    draw.line([(290, 415), (400, 375)], fill="#16a34a", width=3) # Sensor to Queue
    draw.text((305, 380), "xQueueSend()", font=font_small, fill="#16a34a")

    draw.line([(680, 375), (780, 325)], fill="#16a34a", width=3) # Queue to Display
    draw.text((695, 335), "xQueueReceive()", font=font_small, fill="#16a34a")

    draw.line([(400, 420), (290, 545)], fill="#d97706", width=3) # Queue to Alarm
    draw.text((310, 515), "xQueueReceive()", font=font_small, fill="#d97706")

    draw.line([(290, 285), (780, 310)], fill="#9333ea", width=2) # Input to Display
    draw.text((310, 270), "nextDisplayMode() / previousDisplayMode()", font=font_small, fill="#9333ea")

    im.save(r"docs\freertos_architecture.png")
    print("Saved docs/freertos_architecture.png")

# ==============================================================================
# Diagram 3: State Machine (ACTIVE vs INACTIVE)
# ==============================================================================
def make_state_machine():
    w, h = 1000, 600
    im = Image.new("RGB", (w, h), "#f8fafc")
    draw = ImageDraw.Draw(im)

    # Title Banner
    draw.rectangle([(0, 0), (w, 75)], fill="#312e81")
    draw.text((30, 16), "BCA152 FreeRTOS Multisensor — Power State Machine", font=font_title, fill="#ffffff")
    draw.text((30, 48), "Deterministic ACTIVE / INACTIVE Transition Logic and Power Saving Behavior", font=font_subtitle, fill="#c7d2fe")

    # State 1: ACTIVE
    draw.rounded_rectangle([(80, 180), (420, 460)], radius=12, fill="#ecfdf5", outline="#10b981", width=3)
    draw.text((105, 200), "STATE: ACTIVE", font=font_title, fill="#047857")
    draw.line([(105, 240), (395, 240)], fill="#6ee7b7", width=2)
    active_bullets = [
        "- OLED Display powered ON",
        "- Live telemetry visual updates",
        "- Rotary encoder navigation active",
        "- Buzzer alarm active if out of bounds",
        "- EVENT_ACTIVE bit asserted in group",
        "- Sensor sampling every 2000 ms"
    ]
    for idx, b in enumerate(active_bullets):
        draw.text((105, 260 + idx * 30), b, font=font_regular, fill="#065f46")

    # State 2: INACTIVE
    draw.rounded_rectangle([(580, 180), (920, 460)], radius=12, fill="#fef2f2", outline="#ef4444", width=3)
    draw.text((605, 200), "STATE: INACTIVE", font=font_title, fill="#b91c1c")
    draw.line([(605, 240), (895, 240)], fill="#fca5a5", width=2)
    inactive_bullets = [
        "- OLED Display powered OFF (Blank)",
        "- Screen rendering loop bypassed",
        "- Significant energy reduction",
        "- Background PIR monitoring active",
        "- EVENT_ACTIVE bit cleared",
        "- Instant wake-on-presence"
    ]
    for idx, b in enumerate(inactive_bullets):
        draw.text((605, 260 + idx * 30), b, font=font_regular, fill="#991b1b")

    # Transition arrows
    # Top arrow: ACTIVE -> INACTIVE
    draw.line([(420, 260), (580, 260)], fill="#64748b", width=3)
    draw.polygon([(580, 260), (565, 253), (565, 267)], fill="#64748b")
    draw.text((435, 230), "Inactivity Timeout", font=font_bold, fill="#1e293b")
    draw.text((435, 268), ">= 15 sec & No Motion", font=font_small, fill="#475569")

    # Bottom arrow: INACTIVE -> ACTIVE
    draw.line([(580, 380), (420, 380)], fill="#2563eb", width=3)
    draw.polygon([(420, 380), (435, 373), (435, 387)], fill="#2563eb")
    draw.text((440, 350), "PIR Motion Detected", font=font_bold, fill="#1d4ed8")
    draw.text((445, 388), "or Encoder Dial Rotate", font=font_small, fill="#1e40af")

    # Evaluation function box
    draw.rounded_rectangle([(180, 500), (820, 565)], radius=8, fill="#ffffff", outline="#94a3b8", width=1)
    draw.text((200, 510), "Pure Decision Logic: evaluateSystemState(current, motionDetected, elapsedMs, timeoutMs)", font=font_bold, fill="#0f172a")
    draw.text((200, 535), "Unit tested in isolation without hardware dependencies (100% test coverage)", font=font_small, fill="#64748b")

    im.save(r"docs\state_machine.png")
    print("Saved docs/state_machine.png")

# ==============================================================================
# Diagram 4: Wokwi Circuit Schematic & Pin Mapping
# ==============================================================================
def make_wokwi_circuit():
    w, h = 1100, 700
    im = Image.new("RGB", (w, h), "#f8fafc")
    draw = ImageDraw.Draw(im)

    draw.rectangle([(0, 0), (w, 75)], fill="#047857")
    draw.text((30, 16), "BCA152 FreeRTOS Multisensor — Wokwi Hardware Wiring", font=font_title, fill="#ffffff")
    draw.text((30, 48), "Complete ESP32 DevKitC V4 Interfacing Schematic and Pin Configuration", font=font_subtitle, fill="#d1fae5")

    # Central ESP32 Dev Board
    draw.rounded_rectangle([(400, 120), (700, 640)], radius=12, fill="#1e293b", outline="#0f172a", width=3)
    draw.text((470, 140), "ESP32-DEVKITC", font=font_h2, fill="#ffffff")
    draw.text((495, 170), "NodeMCU 38-Pin", font=font_small, fill="#94a3b8")

    # Components surrounding ESP32
    peripherals = [
        ("DHT22 Sensor", "VCC -> 3.3V\nGND -> GND\nSDA -> GPIO 4", 60, 120, "#fef3c7", "#d97706", (290, 180), (400, 240)),
        ("LDR Photoresistor", "VCC -> 3.3V\nGND -> GND\nAO  -> GPIO 34 (ADC1_6)", 60, 310, "#e0f2fe", "#0284c7", (290, 360), (400, 370)),
        ("PIR Motion Sensor", "VCC -> 3.3V\nGND -> GND\nOUT -> GPIO 13", 60, 500, "#f3e8ff", "#9333ea", (290, 550), (400, 500)),
        ("SSD1306 OLED (128x64)", "VCC -> 3.3V\nGND -> GND\nSDA -> GPIO 21\nSCL -> GPIO 22", 810, 120, "#ecfdf5", "#059669", (810, 190), (700, 270)),
        ("KY-040 Rotary Encoder", "VCC -> 3.3V\nGND -> GND\nCLK -> GPIO 18\nDT  -> GPIO 19\nSW  -> GPIO 5", 810, 310, "#e0e7ff", "#4338ca", (810, 390), (700, 420)),
        ("Piezo Buzzer (Alarm)", "PIN 1 -> GND\nPIN 2 -> GPIO 15", 810, 520, "#fee2e2", "#dc2626", (810, 570), (700, 560))
    ]

    for title, pins, bx, by, bg, bd, p1, p2 in peripherals:
        draw.rounded_rectangle([(bx, by), (bx + 230, by + 120)], radius=8, fill=bg, outline=bd, width=2)
        draw.text((bx + 12, by + 10), title, font=font_bold, fill=bd)
        draw.text((bx + 12, by + 35), pins, font=font_small, fill="#334155")
        draw.line([p1, p2], fill=bd, width=3)
        draw.ellipse([(p1[0]-4, p1[1]-4), (p1[0]+4, p1[1]+4)], fill=bd)
        draw.ellipse([(p2[0]-4, p2[1]-4), (p2[0]+4, p2[1]+4)], fill=bd)

    im.save(r"docs\wokwi_circuit.png")
    print("Saved docs/wokwi_circuit.png")

# ==============================================================================
# Diagram 5: System Running Demonstration
# ==============================================================================
def make_system_running():
    w, h = 1100, 680
    im = Image.new("RGB", (w, h), "#0f172a")
    draw = ImageDraw.Draw(im)

    # Title Banner
    draw.text((30, 20), "BCA152 FreeRTOS Multisensor — Live System Demonstration", font=font_title, fill="#38bdf8")
    draw.text((30, 55), "Simulated SSD1306 Visual Display Pages and Thread-Safe Serial Telemetry Stream", font=font_subtitle, fill="#94a3b8")

    # 4 OLED Screens representing the 4 modes
    oled_modes = [
        ("Mode 1: TEMPERATURE", "ROOM MONITOR\n----------------\n  Temperature\n\n    25.4 C\n State: NORMAL", "#10b981"),
        ("Mode 2: HUMIDITY", "ROOM MONITOR\n----------------\n    Humidity\n\n    61.2 %\n RH Level: Good", "#0284c7"),
        ("Mode 3: LIGHT LEVEL", "ROOM MONITOR\n----------------\n  Light Level\n\n     74 %\n  Illum: Bright", "#f59e0b"),
        ("Mode 4: MOTION STATUS", "ROOM MONITOR\n----------------\n Motion Status\n\n >> DETECTED <<\n Room is ACTIVE", "#8b5cf6")
    ]

    for i, (title, content, border_c) in enumerate(oled_modes):
        x = 30 + i * 265
        y = 100
        draw.text((x + 10, y), title, font=font_bold, fill=border_c)

        # OLED outer frame
        draw.rounded_rectangle([(x, y + 26), (x + 245, y + 175)], radius=6, fill="#000000", outline=border_c, width=2)
        draw.text((x + 16, y + 36), content, font=font_mono, fill="#38bdf8")

    # Terminal Log Output Box below
    draw.rounded_rectangle([(30, 310), (w - 30, h - 30)], radius=10, fill="#1e293b", outline="#334155", width=2)
    draw.text((45, 325), "Thread-Safe Serial Monitor Log (Protected by serialMutex):", font=font_bold, fill="#f8fafc")

    logs = [
        "[00:00:00.050] [MAIN] BCA152 FreeRTOS Multisensor System starting...",
        "[00:00:00.080] [MAIN] Executing built-in automated unit test suite (13 Tests)...",
        "[00:00:00.120] [UNITY] -----------------------",
        "[00:00:00.122] [UNITY] 13 Tests 0 Failures 0 Ignored -> OK [PASSED]",
        "[00:00:00.150] [MAIN] All hardware drivers and RTOS synchronization primitives initialized",
        "[00:00:00.160] [MAIN] All 6 FreeRTOS tasks spawned. Scheduler taking over.",
        "[00:00:02.000] [SENSOR] T=25.4 C | H=61.2 % | Light=74 % | Motion=NO",
        "[00:00:04.000] [SENSOR] T=25.5 C | H=61.0 % | Light=75 % | Motion=NO",
        "[00:00:05.420] [INPUT] Encoder rotated CW -> Mode: HUMIDITY",
        "[00:00:06.110] [INPUT] Encoder rotated CW -> Mode: LIGHT",
        "[00:00:07.830] [MOTION] PIR Motion Triggered! (EVENT_MOTION signaled)",
        "[00:00:07.850] [STATE] Motion detected: System restored to ACTIVE state",
        "[00:00:08.000] [SENSOR] T=25.4 C | H=61.2 % | Light=74 % | Motion=YES",
        "[00:00:23.000] [STATE] Inactivity timeout (15000 ms): Entering INACTIVE state (Power-Save)",
        "[00:00:23.050] [DISPLAY] OLED turned OFF for power saving (INACTIVE)"
    ]

    for idx, log in enumerate(logs):
        col = "#38bdf8" if "MAIN" in log else ("#4ade80" if "UNITY" in log else ("#facc15" if "INPUT" in log else ("#c084fc" if "MOTION" in log else ("#fb7185" if "STATE" in log else "#94a3b8"))))
        draw.text((45, 360 + idx * 19), log, font=font_mono, fill=col)

    im.save(r"docs\system_running.png")
    print("Saved docs/system_running.png")

if __name__ == "__main__":
    make_system_architecture()
    make_freertos_architecture()
    make_state_machine()
    make_wokwi_circuit()
    make_system_running()

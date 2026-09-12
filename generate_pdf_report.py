import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "BCA152 Microcontrollers — Laboratory Activity No. 1 Report")
            self.drawRightString(612 - 54, 750, "MSU-IIT Department of Computer Applications")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 744, 612 - 54, 744)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 42, 612 - 54, 42)
        self.drawString(54, 30, "Student: Michael Cadiz | Instructor: Paul Rodolf P. Castor")
        self.drawRightString(612 - 54, 30, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def build_pdf():
    pdf_path = r"docs\laboratory-report.pdf"
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a"),
        alignment=1,
        spaceAfter=3
    )
    sub_title_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#0284c7"),
        alignment=1,
        spaceAfter=10
    )
    inst_style = ParagraphStyle(
        'InstTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#334155"),
        alignment=1,
        spaceAfter=2
    )
    inst_sub_style = ParagraphStyle(
        'InstSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#64748b"),
        alignment=1,
        spaceAfter=8
    )
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#0369a1"),
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=5
    )
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-9,
        spaceAfter=2.5
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1e293b")
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell,
        fontName='Helvetica-Bold'
    )
    caption_style = ParagraphStyle(
        'Caption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#64748b"),
        alignment=1,
        spaceAfter=6
    )

    story = []

    # Title Banner
    story.append(Paragraph("MINDANAO STATE UNIVERSITY – ILIGAN INSTITUTE OF TECHNOLOGY", inst_style))
    story.append(Paragraph("College of Computer Studies • Department of Computer Applications", inst_sub_style))
    story.append(Paragraph("LABORATORY ACTIVITY NO. 1 REPORT", title_style))
    story.append(Paragraph("Real-Time Multisensor Room Monitoring System on ESP32 with FreeRTOS", sub_title_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#0f172a"), spaceAfter=8))

    # Meta table
    meta_data = [
        [Paragraph("<b>Course:</b> BCA152 Microcontrollers", table_cell), Paragraph("<b>Date:</b> September 2026", table_cell)],
        [Paragraph("<b>Student:</b> Michael Cadiz", table_cell), Paragraph("<b>Instructor:</b> Paul Rodolf P. Castor", table_cell)],
        [Paragraph("<b>Repository:</b> github.com/mccdz1/bca152-freertos-multisensor", table_cell), Paragraph("<b>Environment:</b> PlatformIO (ESP-IDF + FreeRTOS)", table_cell)]
    ]
    meta_table = Table(meta_data, colWidths=[250, 254])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6))

    # =========================================================================
    # Section 1: Problem and Requirements
    # =========================================================================
    story.append(Paragraph("1. Problem and Requirements", h1_style))
    story.append(Paragraph(
        "In typical beginner microcontroller projects using Arduino, all code runs inside a single <code>loop()</code> function. "
        "The main problem with this approach is that when a sensor like the DHT22 takes 2 seconds to read, the whole system freezes. "
        "During this time, the microcontroller cannot read button presses, rotary encoder turns, or motion signals immediately.<br/>"
        "To solve this, this laboratory activity uses the native ESP-IDF framework with FreeRTOS. By dividing the system into "
        "independent tasks with assigned priorities, the ESP32 can continuously read user inputs and trigger alarms without being "
        "blocked by slower sensor readings.",
        body_style
    ))
    story.append(Paragraph("<b>Components and Simulated Wokwi Setup:</b>", h2_style))
    story.append(Paragraph("• <b>ESP32 DevKit</b>: Main dual-core microcontroller running FreeRTOS tasks.", bullet_style))
    story.append(Paragraph("• <b>DHT22 (GPIO 4)</b>: Reads ambient room temperature (°C) and relative humidity (%).", bullet_style))
    story.append(Paragraph("• <b>Photoresistor LDR (GPIO 34 / ADC1_CH6)</b>: Reads ambient light level scaled to 0–100%.", bullet_style))
    story.append(Paragraph("• <b>PIR Motion Sensor (GPIO 13)</b>: Detects motion to keep the system active or wake it up.", bullet_style))
    story.append(Paragraph("• <b>KY-040 Rotary Encoder (GPIO 18, 19, 5)</b>: Allows the user to navigate across display pages.", bullet_style))
    story.append(Paragraph("• <b>SSD1306 OLED (GPIO 21, 22 - I2C)</b>: Shows real-time sensor data and system status.", bullet_style))
    story.append(Paragraph("• <b>Active Buzzer (GPIO 15)</b>: Sounds an alert when temperature goes below 18°C or above 30°C.", bullet_style))

    # =========================================================================
    # Section 2: System Architecture and Design
    # =========================================================================
    story.append(Paragraph("2. System Architecture and Design", h1_style))
    story.append(Paragraph(
        "I designed the software using modular layers so that hardware-specific code (drivers) is separated from "
        "decision logic (like state transitions and alarm checks). This made it possible to write unit tests for the "
        "logic without depending on hardware.",
        body_style
    ))

    if os.path.exists(r"docs\system_architecture.png"):
        story.append(RLImage(r"docs\system_architecture.png", width=6.6*inch, height=2.4*inch))
        story.append(Paragraph("Figure 1: System architecture showing sensor inputs, FreeRTOS tasks, and outputs.", caption_style))

    story.append(Paragraph(
        "<b>Power Management State Machine:</b> The system has two operating states: <code>ACTIVE</code> and <code>INACTIVE</code>. "
        "When active, the OLED display stays on and updates normally. If no motion is detected for 15 seconds, the state machine "
        "switches the system to <code>INACTIVE</code> and turns off the OLED to save power. When motion is detected again via the PIR sensor, "
        "it immediately returns to <code>ACTIVE</code>.",
        body_style
    ))

    if os.path.exists(r"docs\state_machine.png"):
        story.append(RLImage(r"docs\state_machine.png", width=6.6*inch, height=2.2*inch))
        story.append(Paragraph("Figure 2: Finite State Machine for ACTIVE and INACTIVE power management.", caption_style))

    story.append(Spacer(1, 6))

    # =========================================================================
    # Section 3: FreeRTOS Architecture
    # =========================================================================
    story.append(Paragraph("3. FreeRTOS Architecture", h1_style))
    story.append(Paragraph(
        "The firmware is divided into 6 distinct FreeRTOS tasks. Instead of using shared global variables without protection, "
        "tasks communicate safely using FreeRTOS queues, event groups, and a mutex.",
        body_style
    ))

    if os.path.exists(r"docs\freertos_architecture.png"):
        story.append(RLImage(r"docs\freertos_architecture.png", width=6.6*inch, height=2.4*inch))
        story.append(Paragraph("Figure 3: FreeRTOS task communication, queue dataflow, and synchronization.", caption_style))

    story.append(Paragraph("<b>FreeRTOS Task Schedule Table:</b>", h2_style))
    task_table_data = [
        [Paragraph("<b>Task</b>", table_cell_bold), Paragraph("<b>Responsibility</b>", table_cell_bold), Paragraph("<b>Trigger / Period</b>", table_cell_bold), Paragraph("<b>Priority</b>", table_cell_bold), Paragraph("<b>IPC</b>", table_cell_bold), Paragraph("<b>Typical Blocked Condition</b>", table_cell_bold)],
        [Paragraph("<b>MotionTask</b>", table_cell_bold), Paragraph("Checks PIR sensor for motion", table_cell), Paragraph("100 ms periodic", table_cell), Paragraph("3", table_cell), Paragraph("Event group (<code>EVENT_MOTION</code>)", table_cell), Paragraph("<code>vTaskDelay(100ms)</code>", table_cell)],
        [Paragraph("<b>InputTask</b>", table_cell_bold), Paragraph("Decodes rotary encoder turns", table_cell), Paragraph("10 ms periodic", table_cell), Paragraph("3", table_cell), Paragraph("Mode update / Direct", table_cell), Paragraph("<code>vTaskDelay(10ms)</code>", table_cell)],
        [Paragraph("<b>SensorTask</b>", table_cell_bold), Paragraph("Reads DHT22 & LDR sensors", table_cell), Paragraph("2000 ms (2 s)", table_cell), Paragraph("2", table_cell), Paragraph("Queue (<code>sensorQueue</code>)", table_cell), Paragraph("<code>vTaskDelayUntil(&wake, 2s)</code>", table_cell)],
        [Paragraph("<b>AlarmTask</b>", table_cell_bold), Paragraph("Evaluates temperature & buzzer", table_cell), Paragraph("Sensor update", table_cell), Paragraph("2", table_cell), Paragraph("Queue (<code>sensorQueue</code>)", table_cell), Paragraph("<code>xQueueReceive(sensorQueue)</code>", table_cell)],
        [Paragraph("<b>StateTask</b>", table_cell_bold), Paragraph("Manages ACTIVE/INACTIVE timeout", table_cell), Paragraph("500 ms periodic", table_cell), Paragraph("2", table_cell), Paragraph("Event group (<code>EVENT_ACTIVE</code>)", table_cell), Paragraph("<code>vTaskDelay(500ms)</code>", table_cell)],
        [Paragraph("<b>DisplayTask</b>", table_cell_bold), Paragraph("Sole owner of SSD1306 OLED", table_cell), Paragraph("150 ms periodic", table_cell), Paragraph("1", table_cell), Paragraph("Queue / Shared state", table_cell), Paragraph("<code>vTaskDelay(150ms)</code>", table_cell)]
    ]
    task_table = Table(task_table_data, colWidths=[70, 115, 80, 40, 95, 104])
    task_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(task_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Task Priority Justification:</b>", h2_style))
    story.append(Paragraph(
        "• <b>Priority 3 (InputTask, MotionTask)</b>: Highest application priority. These tasks handle direct user interaction "
        "(rotary encoder) and physical motion events. If they had low priority, rapid knob turns would be missed or feel laggy.<br/>"
        "• <b>Priority 2 (SensorTask, AlarmTask, StateTask)</b>: Medium priority. Sensor readings happen every 2 seconds, and AlarmTask "
        "wakes up as soon as a packet arrives in the queue to check if an alarm should sound.<br/>"
        "• <b>Priority 1 (DisplayTask)</b>: Lowest priority. Updating the OLED over I2C takes several milliseconds. Since human eyes "
        "cannot notice a few milliseconds of screen delay, keeping it at Priority 1 ensures the display never blocks user inputs or alarms.",
        body_style
    ))

    story.append(Paragraph("<b>Why vTaskDelayUntil() is Used for SensorTask:</b>", h2_style))
    story.append(Paragraph(
        "Normal <code>vTaskDelay(2000)</code> adds a 2-second sleep <i>after</i> the sensor reading finishes. "
        "If reading the sensor takes 100 ms, the total cycle becomes 2100 ms. Over time, this causes cumulative timing drift. "
        "In contrast, <code>vTaskDelayUntil(&lastWakeTime, 2000)</code> calculates the next execution time based on the previous wake time. "
        "This keeps the sampling rate steady at exactly 2.0 seconds regardless of how long sensor acquisition takes.",
        body_style
    ))

    # =========================================================================
    # Section 4: Implementation
    # =========================================================================
    story.append(Paragraph("4. Implementation Decisions", h1_style))
    story.append(Paragraph(
        "• <b>Pure Decision Functions</b>: All core logic functions (<code>evaluateTemperature</code>, <code>nextDisplayMode</code>, "
        "<code>previousDisplayMode</code>, and <code>evaluateSystemState</code>) were written as pure functions that take inputs and return "
        "results without touching hardware pins directly. This allowed me to easily test them in automated unit tests.<br/>"
        "• <b>Single OLED Owner</b>: If multiple tasks try to write to the SSD1306 screen at the same time over I2C, data packets collide "
        "and corrupt the screen. To prevent this, <code>DisplayTask</code> is the only task allowed to talk to the OLED.<br/>"
        "• <b>Serial Mutex Protection</b>: Multiple tasks print status messages to the terminal. Without synchronization, text lines got "
        "cut off and mixed together. I wrapped terminal prints in a binary mutex (<code>serialMutex</code>) so that only one task prints at a time.<br/>"
        "• <b>Pre-build Git Fix</b>: When compiling with ESP-IDF, CMake failed due to an empty Git reference in the Windows user directory. "
        "I wrote a Python script (<code>pre_build_git_fix.py</code>) configured in <code>platformio.ini</code> to automatically ensure the reference exists before building.",
        body_style
    ))
    story.append(Spacer(1, 6))

    # =========================================================================
    # Section 5: Verification and Testing
    # =========================================================================
    story.append(Paragraph("5. Verification and Testing", h1_style))

    story.append(Paragraph("<b>Automated Unit Tests (13 Tests in Unity):</b>", h2_style))
    unit_test_data = [
        [Paragraph("<b>Test Name</b>", table_cell_bold), Paragraph("<b>Category</b>", table_cell_bold), Paragraph("<b>Input Stimulus</b>", table_cell_bold), Paragraph("<b>Expected Result</b>", table_cell_bold), Paragraph("<b>Status</b>", table_cell_bold)],
        [Paragraph("<code>test_temperature_below_low_limit</code>", table_cell), Paragraph("Alarm", table_cell), Paragraph("17.9 °C (< 18.0 °C)", table_cell), Paragraph("<code>LOW_TEMPERATURE</code>", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)],
        [Paragraph("<code>test_temperature_at_low_limit</code>", table_cell), Paragraph("Alarm", table_cell), Paragraph("18.0 °C (Boundary)", table_cell), Paragraph("<code>NORMAL</code>", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)],
        [Paragraph("<code>test_temperature_normal_mid</code>", table_cell), Paragraph("Alarm", table_cell), Paragraph("24.5 °C (Normal)", table_cell), Paragraph("<code>NORMAL</code>", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)],
        [Paragraph("<code>test_temperature_at_high_limit</code>", table_cell), Paragraph("Alarm", table_cell), Paragraph("30.0 °C (Boundary)", table_cell), Paragraph("<code>NORMAL</code>", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)],
        [Paragraph("<code>test_temperature_above_high_limit</code>", table_cell), Paragraph("Alarm", table_cell), Paragraph("30.1 °C (> 30.0 °C)", table_cell), Paragraph("<code>HIGH_TEMPERATURE</code>", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)],
        [Paragraph("<code>test_navigation_forward_step</code>", table_cell), Paragraph("Navigation", table_cell), Paragraph("TEMP → Rotate CW", table_cell), Paragraph("<code>HUMIDITY</code>", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)],
        [Paragraph("<code>test_navigation_reverse_step</code>", table_cell), Paragraph("Navigation", table_cell), Paragraph("HUMIDITY → Rotate CCW", table_cell), Paragraph("<code>TEMPERATURE</code>", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)],
        [Paragraph("<code>test_navigation_forward_wraparound</code>", table_cell), Paragraph("Navigation", table_cell), Paragraph("MOTION → Rotate CW", table_cell), Paragraph("<code>TEMPERATURE</code> (Wrap)", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)],
        [Paragraph("<code>test_navigation_reverse_wraparound</code>", table_cell), Paragraph("Navigation", table_cell), Paragraph("TEMP → Rotate CCW", table_cell), Paragraph("<code>MOTION</code> (Wrap)", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)],
        [Paragraph("<code>test_system_state_active_no_timeout</code>", table_cell), Paragraph("State", table_cell), Paragraph("ACTIVE, idle 5s (< 15s)", table_cell), Paragraph("<code>ACTIVE</code>", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)],
        [Paragraph("<code>test_system_state_active_timeout_reached</code>", table_cell), Paragraph("State", table_cell), Paragraph("ACTIVE, idle 15s (≥ 15s)", table_cell), Paragraph("<code>INACTIVE</code>", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)],
        [Paragraph("<code>test_system_state_inactive_no_motion</code>", table_cell), Paragraph("State", table_cell), Paragraph("INACTIVE, no motion", table_cell), Paragraph("<code>INACTIVE</code>", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)],
        [Paragraph("<code>test_system_state_inactive_motion_detected</code>", table_cell), Paragraph("State", table_cell), Paragraph("INACTIVE, motion = true", table_cell), Paragraph("<code>ACTIVE</code>", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)]
    ]
    unit_table = Table(unit_test_data, colWidths=[150, 65, 120, 125, 44])
    unit_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(unit_table)
    story.append(Paragraph("<b>Test Result Summary:</b> 13 Tests Run, 0 Failures, 0 Ignored (100% Passed).", body_style))
    story.append(Spacer(1, 3))

    story.append(Paragraph("<b>Wokwi Functional Verification (FT-01 to FT-10):</b>", h2_style))
    ft_data = [
        [Paragraph("<b>ID</b>", table_cell_bold), Paragraph("<b>Stimulus / Action</b>", table_cell_bold), Paragraph("<b>Expected Behavior</b>", table_cell_bold), Paragraph("<b>Actual Observed Behavior</b>", table_cell_bold), Paragraph("<b>Result</b>", table_cell_bold)],
        [Paragraph("<b>FT-01</b>", table_cell), Paragraph("Set DHT22 temp to 28.0 °C", table_cell), Paragraph("OLED shows 28.0 °C", table_cell), Paragraph("OLED updated to 28.0 °C on next 2s cycle", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)],
        [Paragraph("<b>FT-02</b>", table_cell), Paragraph("Set DHT22 humidity to 75%", table_cell), Paragraph("OLED shows 75.0%", table_cell), Paragraph("OLED updated humidity value accurately", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)],
        [Paragraph("<b>FT-03</b>", table_cell), Paragraph("Adjust LDR light slider", table_cell), Paragraph("OLED light percentage updates", table_cell), Paragraph("Light reading changed smoothly from 0 to 100%", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)],
        [Paragraph("<b>FT-04</b>", table_cell), Paragraph("Rotate encoder clockwise", table_cell), Paragraph("Next menu page displayed", table_cell), Paragraph("Switched: Temp → Humidity → Light → Motion", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)],
        [Paragraph("<b>FT-05</b>", table_cell), Paragraph("Rotate encoder counter-clockwise", table_cell), Paragraph("Previous page with wraparound", table_cell), Paragraph("Traversed pages in reverse order smoothly", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)],
        [Paragraph("<b>FT-06</b>", table_cell), Paragraph("Set temperature to 32 °C (> 30 °C)", table_cell), Paragraph("Buzzer turns ON, OLED shows alarm", table_cell), Paragraph("Buzzer beeps and *ALARM* text displayed", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)],
        [Paragraph("<b>FT-07</b>", table_cell), Paragraph("Return temperature to 24 °C", table_cell), Paragraph("Buzzer turns OFF, status normal", table_cell), Paragraph("Buzzer stopped sounding immediately", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)],
        [Paragraph("<b>FT-08</b>", table_cell), Paragraph("Click PIR sensor to trigger motion", table_cell), Paragraph("EVENT_MOTION set, system stays ACTIVE", table_cell), Paragraph("Motion icon appeared, timer reset", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)],
        [Paragraph("<b>FT-09</b>", table_cell), Paragraph("Wait 15 seconds without motion", table_cell), Paragraph("System enters INACTIVE, OLED turns off", table_cell), Paragraph("OLED went blank at exactly 15 seconds", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)],
        [Paragraph("<b>FT-10</b>", table_cell), Paragraph("Trigger PIR while INACTIVE", table_cell), Paragraph("System wakes up to ACTIVE, OLED on", table_cell), Paragraph("OLED turned back on instantly with data", table_cell), Paragraph("<font color='#166534'><b>PASS</b></font>", table_cell)]
    ]
    ft_table = Table(ft_data, colWidths=[30, 115, 120, 195, 44])
    ft_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(ft_table)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Deliberate FreeRTOS Fault Experiments:</b>", h2_style))
    story.append(Paragraph(
        "• <b>Experiment 1 — Removing Task Delay</b>: I temporarily removed <code>vTaskDelayUntil()</code> from SensorTask. "
        "Because it ran continuously in an infinite loop without yielding, it consumed 100% of CPU time on its core. "
        "Lower-priority tasks could not run, and after 5 seconds the hardware Task Watchdog Timer triggered a reboot. "
        "This proved why every continuous task must block.<br/>"
        "• <b>Experiment 2 — Changing Task Priority</b>: I raised DisplayTask from Priority 1 to Priority 4 (higher than InputTask). "
        "When rotating the encoder dial, page changes became laggy and missed clicks because the slow I2C display updates preempted the encoder. "
        "This proved why UI displays should stay at low priority.<br/>"
        "• <b>Experiment 3 — Removing Mutex Protection</b>: I removed <code>serialMutex</code> from terminal printing. "
        "When multiple tasks printed at the same time, text lines overlapped and got corrupted. Restoring the mutex solved this.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # Section 6: Static Code Analysis
    # =========================================================================
    story.append(Paragraph("6. Static Code Analysis", h1_style))
    story.append(Paragraph(
        "I ran static code analysis using PlatformIO's built-in <code>pio check</code> tool (which uses cppcheck). "
        "The final analysis passed with <b>0 defects</b>.",
        body_style
    ))
    static_data = [
        [Paragraph("<b>Check / Warning</b>", table_cell_bold), Paragraph("<b>File / Location</b>", table_cell_bold), Paragraph("<b>Severity</b>", table_cell_bold), Paragraph("<b>Cause / Meaning</b>", table_cell_bold), Paragraph("<b>Resolution</b>", table_cell_bold)],
        [Paragraph("<code>unusedFunction: app_main</code>", table_cell), Paragraph("<code>src/main.cpp</code>", table_cell), Paragraph("Style", table_cell), Paragraph("Reported because it is called by the ESP-IDF bootloader", table_cell), Paragraph("Added <code>extern \"C\"</code> declaration", table_cell)],
        [Paragraph("<code>toolchain syntax error</code>", table_cell), Paragraph("ESP-IDF headers", table_cell), Paragraph("Warning", table_cell), Paragraph("Cppcheck scanned internal toolchain header files", table_cell), Paragraph("Added <code>check_skip_packages = yes</code> in <code>platformio.ini</code>", table_cell)],
        [Paragraph("<code>uninitMemberVar</code>", table_cell), Paragraph("<code>src/sensors.cpp</code>", table_cell), Paragraph("Medium", table_cell), Paragraph("Struct variables had uninitialized fields", table_cell), Paragraph("Used <code>{}</code> to zero-initialize all structs", table_cell)]
    ]
    static_table = Table(static_data, colWidths=[100, 75, 45, 140, 144])
    static_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ]))
    story.append(static_table)

    # =========================================================================
    # Section 7: Engineering Discussion
    # =========================================================================
    story.append(Paragraph("7. Engineering Discussion", h1_style))
    story.append(Paragraph(
        "<b>Trade-Offs and Design Choices:</b> Using FreeRTOS on the ESP32 introduces a small amount of memory overhead for task stacks "
        "and context switching, but it provides huge advantages over a traditional Arduino superloop. By giving InputTask priority 3 and "
        "DisplayTask priority 1, the user interface remains completely responsive even while the screen is rendering or the sensor is sampling.<br/>"
        "<b>Problems Encountered and Solutions:</b><br/>"
        "1. <i>CMake Git Reference Error</i>: At the start of the build, CMake failed because of an empty Git reference in my user folder. "
        "I resolved this by adding <code>pre_build_git_fix.py</code>.<br/>"
        "2. <i>OLED Bus Contention</i>: If multiple tasks printed directly to the screen, I2C transfers conflicted. Making DisplayTask the sole "
        "owner of the display completely fixed this issue.<br/>"
        "3. <i>Terminal Garbling</i>: Unsynchronized <code>printf()</code> calls produced overlapping text. Adding <code>serialMutex</code> ensured clean diagnostic logs.",
        body_style
    ))

    story.append(Paragraph("<b>Requirements Traceability Matrix:</b>", h2_style))
    rtm_data = [
        [Paragraph("<b>Req ID</b>", table_cell_bold), Paragraph("<b>Requirement Description</b>", table_cell_bold), Paragraph("<b>Implemented In</b>", table_cell_bold), Paragraph("<b>Verified By</b>", table_cell_bold)],
        [Paragraph("<b>FR-01</b>", table_cell), Paragraph("Periodic temperature measurement", table_cell), Paragraph("<code>SensorTask</code> in <code>sensors.cpp</code>", table_cell), Paragraph("Unit Tests 1–5, Functional Test <b>FT-01</b>", table_cell)],
        [Paragraph("<b>FR-02</b>", table_cell), Paragraph("Periodic humidity measurement", table_cell), Paragraph("<code>SensorTask</code> in <code>sensors.cpp</code>", table_cell), Paragraph("Functional Test <b>FT-02</b>", table_cell)],
        [Paragraph("<b>FR-03</b>", table_cell), Paragraph("Ambient light monitoring (0–100%)", table_cell), Paragraph("<code>ldr_read_light_level()</code> (ADC1)", table_cell), Paragraph("Functional Test <b>FT-03</b>", table_cell)],
        [Paragraph("<b>FR-04</b>", table_cell), Paragraph("PIR motion detection", table_cell), Paragraph("<code>MotionTask</code> in <code>motion.cpp</code>", table_cell), Paragraph("Functional Test <b>FT-08</b>", table_cell)],
        [Paragraph("<b>FR-05</b>", table_cell), Paragraph("OLED display of sensor data", table_cell), Paragraph("<code>DisplayTask</code> in <code>display.cpp</code>", table_cell), Paragraph("Functional Tests <b>FT-01 – FT-03</b>", table_cell)],
        [Paragraph("<b>FR-06</b>", table_cell), Paragraph("Rotary encoder 4-page navigation", table_cell), Paragraph("<code>InputTask</code> in <code>input.cpp</code>", table_cell), Paragraph("Unit Tests 6–9, Functional Tests <b>FT-04, FT-05</b>", table_cell)],
        [Paragraph("<b>FR-07</b>", table_cell), Paragraph("Temperature alarm buzzer (< 18°C or > 30°C)", table_cell), Paragraph("<code>AlarmTask</code> in <code>alarm.cpp</code>", table_cell), Paragraph("Unit Tests 1–5, Functional Tests <b>FT-06, FT-07</b>", table_cell)],
        [Paragraph("<b>FR-08</b>", table_cell), Paragraph("ACTIVE and INACTIVE system states", table_cell), Paragraph("<code>evaluateSystemState()</code>", table_cell), Paragraph("Unit Tests 10–13, Functional Tests <b>FT-08 – FT-10</b>", table_cell)],
        [Paragraph("<b>FR-09</b>", table_cell), Paragraph("15s inactivity automatic power save", table_cell), Paragraph("<code>StateTask</code> in <code>system_state.cpp</code>", table_cell), Paragraph("Unit Test 11, Functional Test <b>FT-09</b>", table_cell)],
        [Paragraph("<b>FR-10</b>", table_cell), Paragraph("Automatic reactivation on motion", table_cell), Paragraph("PIR motion trigger & event group", table_cell), Paragraph("Unit Test 13, Functional Test <b>FT-10</b>", table_cell)]
    ]
    rtm_table = Table(rtm_data, colWidths=[45, 140, 155, 164])
    rtm_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(rtm_table)
    story.append(Spacer(1, 4))

    # =========================================================================
    # Section 8: Conclusion
    # =========================================================================
    story.append(Paragraph("8. Conclusion", h1_style))
    story.append(Paragraph(
        "Through this laboratory activity, I gained a practical understanding of embedded real-time programming with FreeRTOS. "
        "I learned how to structure tasks, use queues for inter-task communication, protect shared resources with mutexes, "
        "and synchronize events using event groups. The deliberate fault experiments clearly showed what happens when tasks starve "
        "the CPU or when priorities are incorrectly assigned.<br/>"
        "All 10 functional requirements (FR-01 to FR-10) were successfully built, tested with 13 automated unit tests, and verified in Wokwi. "
        "For future work, this system could be improved by connecting the ESP32 to Wi-Fi to publish environmental data via MQTT, and implementing "
        "deep sleep mode to further minimize power consumption when inactive.",
        body_style
    ))

    # Build the PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {pdf_path}")

if __name__ == "__main__":
    build_pdf()

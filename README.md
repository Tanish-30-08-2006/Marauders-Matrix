# Tele-ICU Monitoring Matrix

An intelligent clinical dashboard designed for centralized Intensive Care Unit (ICU) telemetry monitoring, proactive risk triage, and early warning detection.

## Overview

The Tele-ICU Matrix addresses clinical alarm fatigue and cognitive overload by categorizing patient vitals into actionable priority tiers:
- **Critical (Red)**: High-risk alerts prioritized by clinical severity and wait time.
- **Watch (Amber)**: Early degradation trends detected before threshold breaches occur.
- **Stable**: Normal telemetry with automated sensor-glitch filtering.

## Key Features

- **Dynamic Triage**: Automatic sorting based on composite risk scores and drift rates.
- **Embedded Sparklines**: Micro-visualizations of vital trends (SpO₂, Heart Rate, Blood Pressure) directly on patient cards.
- **Noise Suppression**: Logs and filters transient artifact glitches to reduce unnecessary alarm alerts.
- **Multi-Hospital View**: Filter by network facility or monitor all beds concurrently.
- **Action Workflow**: Direct bed escalation, team notifications, and audit logging.

## Project Structure

```text
├── frontend/             # Production-tier dashboard with predictive triage
│   ├── matrix.html       # Primary Tele-ICU bed layout
│   ├── detail.html       # In-depth patient telemetry view
│   ├── trends.html       # Longitudinal physiological trends
│   ├── settings.html     # Clinical alarm thresholds & log settings
│   ├── app.js            # Dashboard logic & state handling
│   └── style.css         # Responsive styling
├── frontend_baseline/    # Baseline prototype for comparative evaluation
└── tools/                # Synthetic patient data generators
```

## Getting Started

1. Clone or open the repository.
2. Launch a local static HTTP server:
   ```bash
   python -m http.server 8000
   ```
3. Open `http://localhost:8000/frontend/matrix.html` in your web browser.

# 🏥 Hospital Appointment Management System

Web application for automatic appointment assignment in hospitals in El Salvador, developed with Streamlit.

## Main Features

- 📅 Automatic appointment generation (morning, afternoon, and evening)
- 🏥 Support for multiple hospitals and specialties
- 👥 Complete medical staff management
- 🎉 Holiday registration
- 📊 Dashboard with statistics
- 📁 Export to Excel and CSV

## System Requirements

- Python 3.7+
- Pipenv or virtualenv (recommended)

## Installation

1. Clone the repository:

```bash

git clone https://github.com/augvstTTY/management-hospital-shifts.git

cd management-hospital-shifts

```
2. Install dependencies:

```bash

pip install -r requirements.txt

```

## requirements.txt file

```bash:

streamlit==1.32.2
pandas==2.1.2
numpy==1.26.0
openpyxl==3.1.2
python-dotenv==1.0.0

```

## Project structure

```bash

Hospital/
├── data/
│ ├── personal.json # Personal physician data
│ └── holidays.json # Holidays
├── main.py # Main application
├── README.md # This file
└── requirements.txt # Dependencies

```

## Contributions

Contributions are welcome. Please open an issue or submit a pull request.



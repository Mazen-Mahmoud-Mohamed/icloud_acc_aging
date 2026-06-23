# iCloud Aging Tool

<div align="center">

# 🚀 iCloud Aging Tool

Modern Multi-Threaded iCloud Aging Utility with a CustomTkinter GUI.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![GUI](https://img.shields.io/badge/GUI-CustomTkinter-green)
![Threads](https://img.shields.io/badge/Multi--Threaded-Enabled-orange)
![Status](https://img.shields.io/badge/Status-Active-success)

</div>

---

# 📋 Table of Contents

- Overview
- Features
- Installation
- Requirements
- Configuration
- CSV Format
- Usage
- GUI Features
- Output Files
- Logging System
- Project Structure
- Performance
- Troubleshooting

---

# 📖 Overview

iCloud Aging Tool is a desktop application built with Python and CustomTkinter.

The application provides:

- Modern dark-themed interface
- Multi-threaded processing
- CSV account management
- Progress tracking
- Automatic retries
- Proxy support
- Real-time logging
- Success and failure exports

---

# ✨ Features

## GUI

- Modern CustomTkinter UI
- Responsive layout
- Dark theme
- Colored action buttons
- Progress tracking bar
- Real-time logs

## Processing

- Multi-thread support
- Adjustable thread count
- Automatic retry mechanism
- Stop process at any time
- Background execution

## File Management

- CSV file picker
- Success export
- Failed accounts export
- Automatic file generation

## Logging

- Live status updates
- Success notifications
- Warning messages
- Error tracking

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/your-repository/project.git
cd project
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

Or:

```bash
pip install customtkinter
pip install requests
pip install colorama
pip install termcolor
pip install cryptography
pip install libsrp
```

---

# 📦 Requirements

```txt
customtkinter
requests
cryptography
colorama
termcolor
libsrp
```

---

# 🔧 Configuration

Create a file called:

```ini
config.ini
```

Example:

```ini
[Settings]
use_proxy = false
proxy =
```

Proxy Example:

```ini
[Settings]
use_proxy = true
proxy = socks5://127.0.0.1:9050
```

---

# 📄 CSV Format

Input CSV:

```csv
email,password,birthdate,ans1,ans2,ans3
example@icloud.com,password123,01/01/2008,answer1,answer2,answer3
```

Required columns:

| Column | Description |
|----------|----------|
| email | Apple ID |
| password | Account Password |
| birthdate | Current Birthday |
| ans1 | Security Question 1 |
| ans2 | Security Question 2 |
| ans3 | Security Question 3 |

---

# ▶️ Usage

1. Launch application
2. Select CSV file
3. Set thread count
4. Choose birthday values
5. Click Start Aging
6. Monitor progress
7. Export results automatically

---

# 🖥️ GUI Features

## Main Controls

### Thread Configuration

- Set worker threads
- Improve processing speed

### Birthday Configuration

- Day
- Month
- Year

### CSV Selection

- Browse CSV files
- Validate file selection

### Start Button

- Begins processing
- Locks controls automatically

### Stop Button

- Gracefully stops execution

---

# 📊 Progress Tracking

Features:

- Real-time progress bar
- Account completion tracking
- Percentage completion updates
- Thread-safe UI updates

---

# 📝 Logging System

| Color | Meaning |
|---------|---------|
| 🔵 Blue | Processing |
| 🟢 Green | Success |
| 🟡 Yellow | Retry / Warning |
| 🔴 Red | Error |

Examples:

```text
🔵 Processing account...
🟢 Account completed
🟡 Retrying...
🔴 Failed
```

---

# 📁 Output Files

## aging_success.csv

Contains:

```csv
email,password,birthdate,ans1,ans2,ans3
```

Successfully processed accounts.

---

## accounts.csv

Contains:

Remaining or failed accounts.

---

# 📂 Project Structure

```text
project/
│
├── main.py
├── config.ini
├── accounts.csv
├── aging_success.csv
├── README.md
│
├── utils.py
├── requirements.txt
│
└── modules/
```

---

# ⚡ Performance

Supported:

- Multi-thread execution
- Background processing
- Automatic retries
- Safe UI updates

Recommended:

| Accounts | Threads |
|-----------|-----------|
| 100 | 3-5 |
| 500 | 5-10 |
| 1000+ | 10-20 |

---

# 🛠 Troubleshooting

## Progress Bar Not Visible

Ensure:

```python
progress_frame.pack(...)
progress.pack(...)
```

is executed before:

```python
app.mainloop()
```

---

## Buttons Disabled

Verify:

```python
start_btn.configure(state="normal")
```

and

```python
stop_btn.configure(state="disabled")
```

are called correctly.

---

## CSV Not Loading

Check:

- File exists
- UTF-8 encoding
- Correct column names

---

# 🔒 Stability Features

- Thread-safe callbacks
- Exception handling
- Retry protection
- Graceful shutdown
- Input validation

---

# 👨‍💻 Author

Developed using:

- Python
- CustomTkinter
- Requests
- Cryptography
- Multi-threading

---

<div align="center">

### ⭐ Professional README Generated for GitHub

</div>

# 🛡️ CyberShield — Security Monitoring Dashboard

A beginner-friendly cybersecurity dashboard built with **Python** and **Streamlit**.  
Monitor login activity, detect suspicious IP addresses, and visualise security data — all in one file, no database or machine learning required.

---

## 📸 What It Looks Like

```
🛡️ CyberShield                          ● System Online

┌─────────────┐ ┌──────────────────┐ ┌───────────────┐ ┌──────────────────────┐
│ 🔐 Total    │ │ ✅ Successful    │ │ ❌ Failed     │ │ ⚠️ Suspicious        │
│   Logins    │ │    Logins        │ │    Logins     │ │    Activity          │
│     22      │ │       9          │ │      13       │ │        2             │
└─────────────┘ └──────────────────┘ └───────────────┘ └──────────────────────┘

🔎 Filters
  [Filter by Login Result ▾]     [Filter by Risk Level ▾]

📊 Charts
  [Login Overview — blue bars]   [Failed Attempts by IP — orange bars]

🚨 Flagged IP Addresses
  ⚠️ Suspicious IP Detected: 203.0.113.5   [Risk: 🔴 High]
  ⚠️ Suspicious IP Detected: 198.51.100.77 [Risk: 🔴 High]

📋 Login Records  (sortable table)
```

---

## 🚀 Quick Start

### 1 — Prerequisites

Make sure Python 3.8 or later is installed:

```bash
python --version
```

### 2 — Install dependencies

```bash
pip install streamlit pandas
```

### 3 — Run the dashboard

```bash
streamlit run app.py
```

### 4 — Open your browser

Streamlit will print a URL — open it:

```
Local URL:  http://localhost:8501
```

> **To stop the server** press `Ctrl + C` in the terminal.

---

## 📁 Project Structure

```
📦 project/
 ┣ 📄 app.py                      ← entire application (one file)
 ┣ 📄 README.md                   ← this file
 ┗ 📄 CyberShield_Project_Report.docx  ← full project report
```

---

## ✨ Features

| Feature | Description |
|---|---|
| **Dark dashboard UI** | GitHub-style dark theme (`#0d1117`) with styled metric cards |
| **4 summary cards** | Total logins, Successful, Failed, and Suspicious Activity — all auto-calculated |
| **Rule-based detection** | Flags any IP with **5 or more failed logins** as a brute-force risk |
| **Risk levels** | IPs are rated 🔴 High (5+), 🟠 Medium (3–4), or 🟡 Low (1–2) |
| **Alert warning boxes** | Each flagged IP gets a clear warning explaining why it was flagged |
| **2 interactive charts** | Login Overview (blue) + Failed Attempts by IP (orange) |
| **2 dropdown filters** | Filter by Login Result and by Risk Level — charts update instantly |
| **Raw data table** | Sortable, filterable table of all login records at the bottom |

---

## 🔍 How the Detection Rule Works

```
Step 1 — Load records into a Pandas DataFrame
Step 2 — Group by IP address, count failed attempts per IP
Step 3 — Apply the rule:

         if failed_count >= 5  →  High   (🔴 flagged / suspicious)
         elif failed_count >= 3 →  Medium (🟠 watch list)
         else                  →  Low    (🟡 probably a typo)

Step 4 — Display a warning box for every flagged IP
Step 5 — Update the Suspicious Activity card automatically
```

No machine learning. No external APIs. Just plain Python `if` statements.

---

## 🧪 Sample Data

The app ships with 22 hard-coded login records.  
Two IPs are set up to trigger the detection rule:

| IP Address | Failed Attempts | Risk Level |
|---|---|---|
| `203.0.113.5` | 6 | 🔴 High — flagged |
| `198.51.100.77` | 5 | 🔴 High — flagged (at threshold) |
| `10.0.0.9` | 2 | 🟡 Low |
| `192.168.1.10` | 1 | 🟡 Low |

To experiment, edit the `login_records` list near the top of `app.py` and save — the dashboard recalculates instantly.

---

## 🔧 Customisation

| What to change | Where in `app.py` |
|---|---|
| Add or remove login records | `login_records = [ ... ]` list |
| Change the detection threshold | `THRESHOLD = 5` |
| Change risk level bands | `assign_risk()` function |
| Change chart colours | `color=["#3b82d4"]` / `color=["#f0883e"]` |
| Change the dark theme colours | The `<style>` block at the top |

---

## 📚 Technologies

| Library | Purpose |
|---|---|
| [Python 3.8+](https://www.python.org/) | Core language |
| [Streamlit](https://streamlit.io/) | Web dashboard framework |
| [Pandas](https://pandas.pydata.org/) | Data filtering, grouping, and counting |

---

## 📄 Project Report

A full written report covering the project overview, objectives, feature explanations, detection rule logic, learning outcomes, and future improvements is available in:

```
CyberShield_Project_Report.docx
```

---

## 🗺️ Roadmap / Future Ideas

- [ ] Load records from a CSV file or SQLite database  
- [ ] Add a timestamp field and show login trends over time (line chart)  
- [ ] Add a slider to let users adjust the detection threshold from the dashboard  
- [ ] Send email or Slack alerts when a High-risk IP is detected  
- [ ] Add login/logout authentication to protect the dashboard itself  

---

## 📝 License

This project is for educational purposes. Free to use, modify, and extend.

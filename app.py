import streamlit as st
import pandas as pd

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CyberShield",
    page_icon="🛡️",
    layout="wide",
)

# ── Custom CSS – dark theme ───────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0d1117; color: #e6edf3; }

    /* Hide the default Streamlit header bar */
    header[data-testid="stHeader"] { background: transparent; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 20px 24px;
    }
    [data-testid="metric-container"] label {
        color: #8b949e !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #e6edf3 !important;
        font-size: 2.4rem !important;
        font-weight: 700 !important;
    }

    /* Divider */
    hr { border-color: #21262d; }

    /* Description text */
    .description {
        color: #8b949e;
        font-size: 16px;
        margin-bottom: 8px;
    }

    /* Status badge */
    .badge {
        display: inline-block;
        background-color: #1f6feb22;
        color: #58a6ff;
        border: 1px solid #1f6feb;
        border-radius: 20px;
        padding: 3px 14px;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 24px;
    }

    /* Warning box for flagged IPs */
    .warn-box {
        background-color: #2d1b00;
        border: 1px solid #f0883e;
        border-left: 4px solid #f0883e;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 10px;
        color: #e6edf3;
        font-size: 14px;
        line-height: 1.7;
    }

    /* Section sub-heading */
    .section-title {
        color: #8b949e;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin: 28px 0 10px 0;
    }

    /* Chart container card */
    .chart-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 18px 20px 8px 20px;
        margin-bottom: 4px;
    }

    /* Chart caption text */
    .chart-caption {
        color: #8b949e;
        font-size: 13px;
        margin-top: 4px;
        margin-bottom: 0;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# SAMPLE LOGIN RECORDS
# Each record is a dictionary with three fields:
#   ip      – the IP address of the machine that tried to log in
#   status  – either "success" or "failed"
#   user    – the username that was used
#
# In a real system you would load these from a database or log file.
# Here we just hard-code them so the app works without any external data.
# ════════════════════════════════════════════════════════════════════════════
login_records = [
    # Normal successful logins from various IPs
    {"ip": "192.168.1.10", "status": "success", "user": "alice"},
    {"ip": "192.168.1.11", "status": "success", "user": "bob"},
    {"ip": "192.168.1.12", "status": "success", "user": "carol"},
    {"ip": "10.0.0.5",     "status": "success", "user": "dave"},
    {"ip": "10.0.0.6",     "status": "success", "user": "eve"},

    # A few scattered failed attempts – not enough to be suspicious yet
    {"ip": "192.168.1.10", "status": "failed",  "user": "alice"},
    {"ip": "10.0.0.9",     "status": "failed",  "user": "unknown"},
    {"ip": "10.0.0.9",     "status": "failed",  "user": "unknown"},

    # ── Suspicious IP #1 ────────────────────────────────────────────────────
    # 203.0.113.5 fails 6 times in a row → will be flagged (threshold = 5)
    {"ip": "203.0.113.5",  "status": "failed",  "user": "admin"},
    {"ip": "203.0.113.5",  "status": "failed",  "user": "admin"},
    {"ip": "203.0.113.5",  "status": "failed",  "user": "root"},
    {"ip": "203.0.113.5",  "status": "failed",  "user": "root"},
    {"ip": "203.0.113.5",  "status": "failed",  "user": "administrator"},
    {"ip": "203.0.113.5",  "status": "failed",  "user": "administrator"},

    # ── Suspicious IP #2 ────────────────────────────────────────────────────
    # 198.51.100.77 fails 5 times → exactly at the threshold, will be flagged
    {"ip": "198.51.100.77", "status": "failed", "user": "sysadmin"},
    {"ip": "198.51.100.77", "status": "failed", "user": "sysadmin"},
    {"ip": "198.51.100.77", "status": "failed", "user": "sysadmin"},
    {"ip": "198.51.100.77", "status": "failed", "user": "sysadmin"},
    {"ip": "198.51.100.77", "status": "failed", "user": "sysadmin"},

    # More normal activity after the suspicious attempts
    {"ip": "192.168.1.13", "status": "success", "user": "frank"},
    {"ip": "192.168.1.14", "status": "success", "user": "grace"},
    {"ip": "10.0.0.5",     "status": "success", "user": "dave"},
    {"ip": "10.0.0.6",     "status": "success", "user": "eve"},
]

# ════════════════════════════════════════════════════════════════════════════
# STEP 1 – TURN THE LIST INTO A PANDAS DATAFRAME
# A DataFrame is like a spreadsheet table.
# Each dictionary in login_records becomes one row.
# ════════════════════════════════════════════════════════════════════════════
df = pd.DataFrame(login_records)
# df now has three columns: "ip", "status", "user"

# ════════════════════════════════════════════════════════════════════════════
# STEP 2 – COUNT FAILED LOGINS PER IP AND ASSIGN A RISK LEVEL
# We group the DataFrame by IP, count failures, then label each IP as:
#   High   – 5 or more failed attempts  (crosses the brute-force threshold)
#   Medium – 3 or 4 failed attempts     (worth watching)
#   Low    – 1 or 2 failed attempts     (probably just a typo)
# ════════════════════════════════════════════════════════════════════════════
THRESHOLD = 5   # same rule as before – 5+ failures = suspicious

# Group all rows where status == "failed", count how many per IP
failed_df = (
    df[df["status"] == "failed"]   # keep only failed rows
    .groupby("ip")                 # group identical IPs together
    .size()                        # count the rows in each group
    .reset_index(name="failed_count")  # give the count column a name
)
# failed_df looks like:
#            ip  failed_count
#  192.168.1.10             1
#     10.0.0.9              2
#  203.0.113.5              6
# 198.51.100.77             5

# Assign a risk level to each IP using a simple if/elif/else function
def assign_risk(count):
    """Return a risk label based on how many times this IP failed."""
    if count >= 5:
        return "High"
    elif count >= 3:
        return "Medium"
    else:
        return "Low"

# Apply the function to every row in the failed_count column
# This creates a new "risk" column in failed_df
failed_df["risk"] = failed_df["failed_count"].apply(assign_risk)

# ════════════════════════════════════════════════════════════════════════════
# STEP 3 – COUNT TOTALS (same logic as before, now using pandas)
# ════════════════════════════════════════════════════════════════════════════
total_logins      = len(df)
successful_logins = len(df[df["status"] == "success"])
failed_logins     = len(df[df["status"] == "failed"])

# Flagged IPs are those with High risk (failed_count >= THRESHOLD)
flagged_ips   = failed_df[failed_df["risk"] == "High"].to_dict("records")
suspicious_acts = len(flagged_ips)

# ════════════════════════════════════════════════════════════════════════════
# DASHBOARD UI
# ════════════════════════════════════════════════════════════════════════════

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 🛡️ CyberShield")
st.markdown('<div class="badge">● System Online</div>', unsafe_allow_html=True)
st.markdown(
    '<p class="description">'
    "Real-time security monitoring dashboard — track login activity and "
    "detect suspicious behaviour across your network."
    "</p>",
    unsafe_allow_html=True,
)
st.divider()

# ── Four metric cards ─────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric(label="🔐  Total Logins",        value=f"{total_logins:,}")
col2.metric(label="✅  Successful Logins",   value=f"{successful_logins:,}")
col3.metric(label="❌  Failed Logins",       value=f"{failed_logins:,}")
col4.metric(label="⚠️  Suspicious Activity", value=f"{suspicious_acts:,}")

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# FILTERS
# st.selectbox() creates a dropdown menu.
# The chosen value is stored in a variable and used below to filter data.
# Both filters sit side-by-side in two columns.
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-title">🔎 Filters</p>', unsafe_allow_html=True)

fcol1, fcol2 = st.columns(2)

with fcol1:
    # Filter 1 – Login Result
    # Lets the user view all records, only successes, or only failures.
    # This filter affects the login overview bar chart and the raw data table.
    result_filter = st.selectbox(
        label="Filter by Login Result",
        options=["All", "success", "failed"],
        help="Show all login attempts, or narrow down to successes or failures only.",
    )

with fcol2:
    # Filter 2 – Risk Level
    # Lets the user focus the 'Failed Attempts by IP' chart and alert list
    # on a specific risk band (High / Medium / Low).
    risk_filter = st.selectbox(
        label="Filter by Risk Level",
        options=["All", "High", "Medium", "Low"],
        help="High = 5+ failures (brute-force risk), Medium = 3–4, Low = 1–2.",
    )

# ════════════════════════════════════════════════════════════════════════════
# APPLY FILTERS TO THE DATA
# We create filtered copies of the DataFrames here.
# The original df and failed_df are never changed.
# ════════════════════════════════════════════════════════════════════════════

# Apply login-result filter to the main DataFrame
if result_filter == "All":
    filtered_df = df                          # no filter – show everything
else:
    filtered_df = df[df["status"] == result_filter]  # keep only matching rows

# Apply risk-level filter to the failed-IPs DataFrame
if risk_filter == "All":
    filtered_failed_df = failed_df            # no filter – show all IPs
else:
    filtered_failed_df = failed_df[failed_df["risk"] == risk_filter]

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# CHARTS
# Two charts sit side by side.
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-title">📊 Charts</p>', unsafe_allow_html=True)

chart_col1, chart_col2 = st.columns(2)

# ── Chart 1: Login Overview (Successful vs Failed) ───────────────────────────
# HOW IT HELPS:
#   This chart gives you an instant visual comparison between normal
#   (successful) logins and problem (failed) logins.
#   A healthy system has a tall green bar and a very short red bar.
#   If the red bar grows close to the green one, something is wrong.
#   The result_filter dropdown controls which bars are shown.
with chart_col1:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown("**Login Overview**")

    # Count how many success and failed rows exist in the filtered data
    overview_counts = filtered_df["status"].value_counts().reset_index()
    overview_counts.columns = ["Login Result", "Count"]

    # st.bar_chart() draws the chart automatically from a DataFrame.
    # We rename the column to "Count" so the axis label makes sense.
    st.bar_chart(
        overview_counts.set_index("Login Result"),
        color=["#3b82d4"],   # single blue colour for the bars
        height=280,
    )
    st.markdown(
        '<p class="chart-caption">'
        "Compares the number of successful vs failed login attempts. "
        "A large failed bar may indicate an ongoing attack."
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ── Chart 2: Failed Attempts by IP Address ───────────────────────────────────
# HOW IT HELPS:
#   This chart shows WHICH specific IP addresses are generating failures
#   and HOW MANY failures each one has.
#   One IP with a very tall bar is a red flag — it suggests a single
#   machine is repeatedly trying to break into your system (brute-force).
#   The risk_filter dropdown narrows this chart to one risk band at a time.
with chart_col2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown("**Failed Login Attempts by IP Address**")

    if filtered_failed_df.empty:
        # If the filter returns no rows, show a friendly message instead of
        # an empty or broken chart.
        st.info("No failed login data matches the selected risk filter.")
    else:
        # Use the filtered failed_df; set IP as the index so bars are labelled
        st.bar_chart(
            filtered_failed_df.set_index("ip")[["failed_count"]],
            color=["#f0883e"],   # orange bars to signal danger
            height=280,
        )

    st.markdown(
        '<p class="chart-caption">'
        "Shows how many times each IP address failed to log in. "
        "IPs with 5 or more failures are flagged as High risk (brute-force)."
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# FLAGGED IP ALERTS
# We re-use the risk_filter here so the alert list matches the chart above.
# If the user picks "High", only High-risk IPs are shown.
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-title">🚨 Flagged IP Addresses</p>', unsafe_allow_html=True)

# Decide which IPs to show in the alert section based on risk_filter
if risk_filter == "All":
    # Show only High-risk IPs in the alert section (they are the dangerous ones)
    alerts_to_show = failed_df[failed_df["risk"] == "High"].to_dict("records")
else:
    # Show IPs matching the selected risk band
    alerts_to_show = filtered_failed_df.to_dict("records")

if len(alerts_to_show) > 0:
    for item in alerts_to_show:
        ip    = item["ip"]
        count = item["failed_count"]
        risk  = item["risk"]

        # Choose a label colour based on risk level
        if risk == "High":
            risk_badge = "🔴 High"
        elif risk == "Medium":
            risk_badge = "🟠 Medium"
        else:
            risk_badge = "🟡 Low"

        warning_html = f"""
        <div class="warn-box">
            <strong>⚠️ Suspicious IP Detected: {ip}</strong>
            &nbsp;&nbsp;<span style="font-size:13px;">[Risk: {risk_badge}]</span><br>
            <strong>Reason:</strong> This IP address had <strong>{count} failed login
            attempt{"s" if count != 1 else ""}</strong>, which places it in the
            <strong>{risk}</strong> risk category
            (threshold for High = {THRESHOLD} failures).<br>
            <strong>Risk:</strong> A high number of failed attempts from the same IP
            often indicates a brute-force attack — someone trying many passwords
            until one works.<br>
            <strong>Recommended action:</strong> Block this IP address and review
            the login logs for the accounts it targeted.
        </div>
        """
        st.markdown(warning_html, unsafe_allow_html=True)

else:
    st.success("✅ No flagged IP addresses match the selected filters.")

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# RAW DATA TABLE
# Shows the underlying login records filtered by the Login Result dropdown.
# Useful for manual inspection of the raw data behind the charts.
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-title">📋 Login Records</p>', unsafe_allow_html=True)
st.caption(
    f"Showing {len(filtered_df)} of {total_logins} records "
    f"(filter: {result_filter})"
)
st.dataframe(
    filtered_df.reset_index(drop=True),
    use_container_width=True,
    hide_index=True,
)

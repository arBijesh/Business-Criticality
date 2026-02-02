import streamlit as st
import pandas as pd

# Page Config
st.set_page_config(page_title="AEP App Scorer (Expanded)", layout="centered")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .big-font { font-size:18px !important; }
    .stRadio > label { font-size: 16px; font-weight: bold; color: #2c3e50; }
    .stSelectbox > label { font-size: 16px; font-weight: bold; color: #2c3e50; }
    div[data-testid="stForm"] { border: 2px solid #f0f2f6; padding: 25px; border-radius: 10px; }
    h3 { color: #1565C0; padding-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIC ENGINE ---
def calculate_score(a):
    # TIER 1: MISSION CRITICAL (Red)
    # Logic: Safety, Grid, Immediate Fines, or Emergency Restore (<4 hrs)
    if (a['Safety'] == 'Yes' or 
        a['Grid'] == 'Yes' or 
        a['Fines'] == 'Yes' or 
        a['RestoreTime'] == 'Immediately (Within 4 hours)'):
        return {
            "Level": "1 - Mission Critical",
            "Description": "Vital for Safety, Grid, or Law. Zero downtime tolerance.",
            "Color": "#D32F2F"
        }

    # TIER 2: BUSINESS CRITICAL (Orange)
    # Logic: Money, Customers, Privacy, or "Same Day" restore
    if (a['Money'] == 'Yes' or 
        a['Public'] == 'Yes' or 
        a['Privacy'] == 'Yes' or 
        a['RestoreTime'] == 'Same Day (Within 24 hours)'):
        return {
            "Level": "2 - Business Critical",
            "Description": "Core business blocked. High financial or reputation risk.",
            "Color": "#F57C00"
        }

    # TIER 3: OPERATIONAL (Blue)
    # Logic: Wide usage (Whole Company) OR Daily usage with no backup
    if (a['Users'] == 'The Whole Company (Everyone)' or 
        (a['UsageFreq'] == 'Daily / Constantly' and a['ManualBackup'] == 'No')):
        return {
            "Level": "3 - Operational",
            "Description": "Important for daily work. High inconvenience if down.",
            "Color": "#1976D2"
        }

    # TIER 4: NON-CRITICAL (Grey)
    return {
        "Level": "4 - Non-Critical",
        "Description": "Administrative or convenience tool. Work continues without it.",
        "Color": "#616161"
    }

# --- HEADER ---
st.title("⚡ Expanded App Assessment")
st.write("Please answer these **16 questions**. This helps us understand who needs this app, how risky it is, and how to support it.")

# --- INPUTS ---
with st.form("expanded_form"):
    
    # 0. BASIC INFO
    col_a, col_b = st.columns(2)
    with col_a:
        app_name = st.text_input("Application Name (e.g. OMS, SAP)")
    with col_b:
        dept_name = st.selectbox("Department", ["Distribution", "Transmission", "Generation", "IT/Corporate", "HR/Finance"])

    st.divider()

    # SECTION 1: THE "KILL SWITCH" (Impact)
    st.markdown("### 1. 🚨 The 'Kill Switch' (Impact)")
    
    q1_safety = st.radio("1. Could a failure here hurt a person or damage the Power Grid?", ["No", "Yes"], horizontal=True)
    q2_money = st.radio("2. Do we lose actual money (revenue/payments) if this breaks?", ["No", "Yes"], horizontal=True)
    q3_fines = st.radio("3. Will the government fine or sue us immediately if this is down?", ["No", "Yes"], horizontal=True)
    q4_restore = st.selectbox("4. If it breaks, how fast do you need it back?", 
                              ["Immediately (Within 4 hours)", "Same Day (Within 24 hours)", "Next Day (24-48 hours)", "3-5 Days (Low Priority)"])

    st.divider()

    # SECTION 2: THE PEOPLE (Usage)
    st.markdown("### 2. 👥 The People (Usage)")
    
    q5_users = st.selectbox("5. Who uses this software?", 
                            ["Just me / My small team (<10 people)", "My whole department (~50-100 people)", "The Whole Company (Everyone)"])
    q6_freq = st.radio("6. How often do people log in?", ["Rarely / Once a Month", "Weekly", "Daily / Constantly"], horizontal=True)
    q7_public = st.radio("7. Do external Customers (the public) use this directly?", ["No", "Yes"], horizontal=True)
    q8_backup = st.radio("8. Can you do your job on Paper/Excel if this breaks?", ["Yes (We can survive manually)", "No (We stop working)"], horizontal=True)

    st.divider()

    # SECTION 3: THE TECH (Hosting & Support)
    st.markdown("### 3. 💻 The Tech (Hosting)")
    
    q9_access = st.radio("9. How do you access it?", ["Web Browser (Chrome/Edge)", "Installed on my Laptop (.exe)", "Mobile App on Phone"], horizontal=True)
    q10_login = st.radio("10. Do you log in with your standard AEP Password?", ["Yes (SSO)", "No (Separate Username/Password)"], horizontal=True)
    q11_vendor = st.selectbox("11. Who built this?", ["We bought it (Vendor/SaaS)", "AEP built it (In-house Custom)", "I don't know"])
    q12_network = st.radio("12. Does it work without the Internet/Network?", ["No (Needs Network)", "Yes (Works Offline)"], horizontal=True)

    st.divider()

    # SECTION 4: THE DATA (Security & Connections)
    st.markdown("### 4. 🔒 The Data")

    q13_privacy = st.radio("13. Does it contain private people data (SSN, Payroll, Addresses)?", ["No", "Yes"], horizontal=True)
    q14_export = st.radio("14. Can you export data to Excel/PDF from it?", ["No", "Yes"], horizontal=True)
    q15_connect = st.radio("15. Does it send data automatically to other AEP systems?", ["No (It stands alone)", "Yes (It feeds other apps)"], horizontal=True)
    q16_input = st.radio("16. Do you TYPE new data in, or just READ old data?", ["We Type/Edit Data (Active)", "Just Read/View (Read-Only)"], horizontal=True)

    st.divider()
    submitted = st.form_submit_button("Check Criticality Level")

# --- RESULTS ---
if submitted:
    if not app_name:
        st.error("⚠️ Please enter an Application Name at the top.")
    else:
        # Collect Answers
        answers = {
            "Safety": q1_safety, "Grid": q1_safety, 
            "Money": q2_money, "Fines": q3_fines, "RestoreTime": q4_restore,
            "Users": q5_users, "UsageFreq": q6_freq, "Public": q7_public, "ManualBackup": q8_backup,
            "Access": q9_access, "Login": q10_login, "Vendor": q11_vendor, "Network": q12_network,
            "Privacy": q13_privacy, "Export": q14_export, "Connects": q15_connect, "Input": q16_input
        }

        # Calculate Score
        result = calculate_score(answers)

        # Show Visual Result
        st.success("Assessment Complete!")
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 15px solid {result['Color']};">
            <h2 style="color: {result['Color']}; margin:0;">{result['Level']}</h2>
            <p style="font-size: 18px; margin-top: 10px;">{result['Description']}</p>
        </div>
        """, unsafe_allow_html=True)

        # --- PREPARE EXCEL LIST (2 Columns) ---
        data_rows = [
            ["Application Name", app_name],
            ["Department", dept_name],
            ["CALCULATED CRITICALITY", result['Level']],
            ["--- SECTION 1: IMPACT ---", ""],
            ["1. Safety/Grid Risk", q1_safety],
            ["2. Financial Loss", q2_money],
            ["3. Legal/Fines", q3_fines],
            ["4. Required Restore Time", q4_restore],
            ["--- SECTION 2: USAGE ---", ""],
            ["5. Who uses it?", q5_users],
            ["6. How often?", q6_freq],
            ["7. External Customers?", q7_public],
            ["8. Manual Workaround?", q8_backup],
            ["--- SECTION 3: TECH ---", ""],
            ["9. Access Method", q9_access],
            ["10. Login Method (SSO)", q10_login],
            ["11. Vendor/Builder", q11_vendor],
            ["12. Network Dependency", q12_network],
            ["--- SECTION 4: DATA ---", ""],
            ["13. PII/Private Data", q13_privacy],
            ["14. Export Capability", q14_export],
            ["15. Integration (Feeds others)", q15_connect],
            ["16. Read-Only vs Active", q16_input]
        ]

        # Convert to DataFrame
        df = pd.DataFrame(data_rows, columns=["Question", "Answer"])

        # Display Table
        st.markdown("### 📥 Verify & Download")
        st.dataframe(df, hide_index=True, use_container_width=True)

        # Download Button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Results (Excel/CSV)",
            data=csv,
            file_name=f"{app_name}_Full_Assessment.csv",
            mime="text/csv"
        )

import streamlit as st
import pandas as pd

# Set page configuration
st.set_page_config(page_title="AEP Application Criticality Assessor", layout="wide")

def calculate_criticality(responses):
    """
    AEP Specific Logic:
    1. Mission Critical: Grid Control, NERC CIP, Safety, Storm Response.
    2. Business Critical: Revenue (Billing), Customer Service, Supply Chain.
    3. Non-Critical: Internal Admin.
    4. Archive: Legacy.
    """
    
    # --- TIER 1: MISSION CRITICAL (Grid & Safety) ---
    # Logic: If it controls the grid, is NERC regulated, affects Nuclear safety, 
    # or is critical for Storm Restoration -> It is Mission Critical.
    if (responses['grid_control'] == 'Yes' or 
        responses['nerc_cip'] == 'Yes' or 
        responses['nuclear_safety'] == 'Yes' or 
        responses['storm_restoration'] == 'Yes' or
        responses['safety_impact'] == 'Yes'):
        return {
            "tier": "Tier 1: MISSION CRITICAL",
            "color": "#D32F2F",  # Red
            "definition": "Impacts Grid Reliability, Public Safety, or NERC Compliance.",
            "rto": "< 1 hour (Real-time)",
            "support": "24/7 Dedicated Command Center",
            "examples": "SCADA, EMS, Outage Management System (OMS), GIS (Grid Maps)"
        }

    # --- TIER 1.5/2: BUSINESS CRITICAL (Financial & Customer) ---
    # Logic: Huge Financial loss or Call Center down (can't take outage calls)
    if (responses['financial_loss'] == 'Yes' or 
        responses['regulatory_fines'] == 'Yes' or
        (responses['stops_work'] == 'Yes' and responses['workaround_exists'] == 'No')):
        return {
            "tier": "Tier 2: BUSINESS CRITICAL",
            "color": "#F57C00",  # Orange
            "definition": "Core business operations stop. Revenue/Customer Service impacted.",
            "rto": "< 4 hours",
            "support": "Business Hours + On-call",
            "examples": "Customer Billing (CIS), Smart Meter Data (AMI), Work Management (Maximo)"
        }

    # --- TIER 3: NON-CRITICAL (Internal) ---
    if responses['inconvenient_only'] == 'Yes' or responses['stops_work'] == 'No':
        return {
            "tier": "Tier 3: NON-CRITICAL (Internal)",
            "color": "#1976D2",  # Blue
            "definition": "Internal productivity impacted, but lights stay on.",
            "rto": "24-48 hours",
            "support": "Best Effort (Next Business Day)",
            "examples": "Employee Intranet (The Wire), Room Booking, Training Portals"
        }

    # --- TIER 4: ARCHIVE ---
    return {
        "tier": "Tier 4: ADMINISTRATIVE / ARCHIVE",
        "color": "#616161",  # Grey
        "definition": "Rarely used or read-only data.",
        "rto": "> 1 week",
        "support": "No SLA",
        "examples": "Legacy Historical Data, Test/Dev Sandboxes"
    }

# --- APP UI ---

col_logo, col_title = st.columns([1, 5])
with col_title:
    st.title("⚡ AEP Business Criticality Assessor")
st.markdown("""
This tool defines application criticality based on **Grid Reliability**, **NERC Compliance**, and **Business Impact**.
""")

st.divider()

# Input: Application Details
with st.sidebar:
    st.header("Application Details")
    app_name = st.text_input("Application Name")
    app_owner = st.text_input("Application Owner")
    business_unit = st.selectbox("Business Unit", 
        ["Transmission", "Distribution", "Generation", "Customer Service", "Corporate IT", "Nuclear"])

# Container for the Form
with st.form("assessment_form"):
    
    # SECTION A: UTILITY SPECIFIC (The most important for AEP)
    st.subheader("1. Grid & Public Safety (Utility Specific)")
    st.info("These questions determine if the app impacts the physical power grid.")
    c1, c2 = st.columns(2)
    with c1:
        q_grid = st.radio("Does this app directly control/monitor Grid Operations (SCADA/EMS)?", ("No", "Yes"), index=0)
        q_nerc = st.radio("Is this system in scope for NERC CIP compliance?", ("No", "Yes"), index=0, help="Federal fines apply if this system is breached or down.")
    with c2:
        q_storm = st.radio("Is this app critical for Storm Restoration (dispatching trucks/crews)?", ("No", "Yes"), index=0)
        q_nuc = st.radio("Does this impact Nuclear Generation safety?", ("No", "Yes"), index=0)

    st.divider()

    # SECTION B: FINANCIAL & GENERAL SAFETY
    st.subheader("2. Financial, Regulatory & Corporate Safety")
    c3, c4 = st.columns(2)
    with c3:
        q_fin = st.radio("Does an outage cause immediate major financial loss (> $100k/hr)?", ("No", "Yes"), index=0)
        q_reg = st.radio("Are there other regulatory fines (non-NERC) e.g., SOX/EPA?", ("No", "Yes"), index=0)
    with c4:
        q_safe = st.radio("Does the outage impact field worker safety (Arc flash data, etc.)?", ("No", "Yes"), index=0)

    st.divider()

    # SECTION C: OPERATIONAL
    st.subheader("3. Operational Impact")
    c5, c6 = st.columns(2)
    with c5:
        q_stop = st.radio("Does an outage STOP work for critical teams (e.g., Call Center)?", ("No", "Yes"), index=0)
    with c6:
        q_work = st.radio("Is there a viable manual workaround?", ("No", "Yes"), index=0)

    # SECTION D: CONVENIENCE
    st.divider()
    st.subheader("4. Usage")
    q_conv = st.radio("Is the outage merely 'inconvenient' (e.g., cafeteria menu)?", ("No", "Yes"), index=0)

    # Submit Button
    submitted = st.form_submit_button("Assess AEP Criticality")

# --- RESULTS PROCESSING ---
if submitted:
    if not app_name:
        st.warning("Please enter an Application Name in the sidebar.")
    else:
        # Collect responses
        user_responses = {
            "grid_control": q_grid,
            "nerc_cip": q_nerc,
            "storm_restoration": q_storm,
            "nuclear_safety": q_nuc,
            "financial_loss": q_fin,
            "regulatory_fines": q_reg,
            "safety_impact": q_safe,
            "stops_work": q_stop,
            "workaround_exists": q_work,
            "inconvenient_only": q_conv
        }
        
        # Calculate Logic
        result = calculate_criticality(user_responses)
        
        st.divider()
        st.subheader(f"Assessment Result: {app_name}")
        
        # Display Result Card
        st.markdown(f"""
        <div style="padding: 20px; border-radius: 10px; background-color: #f0f2f6; border-left: 10px solid {result['color']};">
            <h2 style="color: {result['color']}; margin:0;">{result['tier']}</h2>
            <p style="font-size: 18px;"><strong>Definition:</strong> {result['definition']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display Details
        c1, c2, c3 = st.columns(3)
        c1.metric("Recovery Time (RTO)", result['rto'])
        c2.metric("Support Level", result['support'])
        c3.info(f"**AEP Examples:** {result['examples']}")

        # JSON Export
        st.download_button(
            label="Download JSON",
            data=pd.Series({**{"Application": app_name}, **user_responses, **result}).to_json(),
            file_name=f"{app_name}_AEP_assessment.json",
            mime="application/json"
        )

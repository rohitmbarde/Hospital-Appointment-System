import os
import json
from datetime import datetime
import streamlit as st
import requests

API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")

# Professional Healthcare Theme Configuration
st.set_page_config(
    page_title="Get Life Hospital - Appointment System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Healthcare Theme
st.markdown("""
<style>
    /* Main theme colors - Healthcare Blue & Green */
    :root {
        --primary-color: #0066CC;
        --secondary-color: #00A86B;
        --bg-color: #F0F8FF;
        --card-bg: #FFFFFF;
    }
    
    /* Header styling - Compact */
    .main-header {
        background: linear-gradient(135deg, #0066CC 0%, #00A86B 100%);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .hospital-name {
        color: white;
        font-size: 1.8rem;
        font-weight: bold;
        margin: 0;
        text-align: center;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    .hospital-tagline {
        color: white;
        font-size: 0.9rem;
        text-align: center;
        margin-top: 0.3rem;
        font-weight: 300;
    }
    
    /* Card styling */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #0066CC;
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #0066CC 0%, #00A86B 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border-radius: 5px;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,102,204,0.3);
    }
    
    /* Section headers */
    h2, h3 {
        color: #0066CC;
        border-bottom: 2px solid #00A86B;
        padding-bottom: 0.5rem;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 8px;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #F0F8FF;
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Welcome message - Compact */
    .welcome-box {
        background: linear-gradient(135deg, #E6F3FF 0%, #E6FFF5 100%);
        padding: 0.8rem 1rem;
        border-radius: 6px;
        text-align: center;
        margin: 0.5rem 0 1rem 0;
        border: 1px solid #00A86B;
    }
    
    .welcome-text {
        font-size: 1rem;
        color: #0066CC;
        font-weight: 600;
        margin: 0;
    }
    
    .sub-welcome {
        color: #00A86B;
        font-size: 0.85rem;
        margin-top: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# Hospital Header
st.markdown("""
<div class="main-header">
    <h1 class="hospital-name">🏥 Get Life Hospital</h1>
    <p class="hospital-tagline">Your Health, Our Priority - Advanced Healthcare Services</p>
</div>
""", unsafe_allow_html=True)

# Welcome Message
st.markdown("""
<div class="welcome-box">
    <p class="welcome-text">Welcome to Get Life Hospital Appointment System</p>
    <p class="sub-welcome">✨ Book your appointment with our expert doctors in just a few clicks</p>
</div>
""", unsafe_allow_html=True)


def post_json(path: str, payload: dict):
    resp = requests.post(f"{API_BASE}{path}", json=payload)
    if resp.status_code >= 400:
        raise RuntimeError(resp.json().get("detail", resp.text))
    return resp.json()


def get_json(path: str, headers=None, params=None):
    resp = requests.get(f"{API_BASE}{path}", headers=headers, params=params)
    if resp.status_code >= 400:
        raise RuntimeError(resp.json().get("detail", resp.text))
    return resp.json()


# Role Selection with Icons - Compact
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    pass
with col2:
    col_a, col_b = st.columns(2)
    with col_a:
        patient_selected = st.button("👤 Patient", use_container_width=True, type="primary")
    with col_b:
        admin_selected = st.button("🔐 Admin", use_container_width=True)
with col3:
    pass

# Store role in session state
if patient_selected:
    st.session_state["role"] = "Patient"
if admin_selected:
    st.session_state["role"] = "Admin"

role = st.session_state.get("role", "Patient")

if role == "Patient":
    # Patient Portal Header - Compact
    st.markdown("""
    <div style="background: linear-gradient(90deg, #0066CC 0%, #00A86B 100%); padding: 0.6rem; border-radius: 6px; margin: 0.5rem 0;">
        <h3 style="color: white; margin: 0; text-align: center; font-size: 1.2rem;">👤 Patient Portal</h3>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("triage_form"):
        st.subheader("📝 Patient Information")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("👤 Full Name *", placeholder="Enter your full name")
            age = st.number_input("🎂 Age *", min_value=0, max_value=120, value=30)
        with col2:
            gender = st.selectbox("⚧ Gender *", ["", "Male", "Female", "Other"], index=0)
            email = st.text_input("📧 Email Address *", placeholder="your.email@example.com")
        
        st.subheader("🩺 Medical Information")
        symptoms = st.text_area(
            "💬 Describe Your Symptoms *", 
            placeholder="Please describe your symptoms in detail (e.g., 'Having severe headache since morning', 'Chest pain with shortness of breath', etc.)",
            height=120
        )
        
        st.caption("* Required fields")
        
        submitted = st.form_submit_button("🔍 Analyze Symptoms & Find Doctor", use_container_width=True, type="primary")

    if submitted:
        if not name or not email or not symptoms:
            st.error("❌ Please fill in all required fields!")
        else:
            with st.spinner("🔍 Analyzing your symptoms and finding the best specialist..."):
                try:
                    result = post_json(
                        "/api/patient/triage",
                        {
                            "patient": {"name": name, "age": age, "gender": gender or None, "email": email},
                            "symptoms": symptoms,
                        },
                    )
                    st.success("✅ Analysis Complete! We've found the right specialist for you.")
                    st.session_state["triage_result"] = result
                    st.session_state["last_symptoms"] = symptoms
                except Exception as exc:
                    st.error(f"❌ Error: {str(exc)}")

    triage_result = st.session_state.get("triage_result")
    if triage_result:
        st.divider()
        
        # Analysis Results in Card Format
        st.markdown("""
        <div style="background: linear-gradient(90deg, #00A86B 0%, #0066CC 100%); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <h2 style="color: white; margin: 0; text-align: center;">🩺 Medical Analysis Results</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Show message if LLM provided special guidance
        if triage_result.get("message"):
            st.warning(f"ℹ️ **Important Note:** {triage_result['message']}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="info-card">
                <h3>🏥 Department</h3>
                <p style="font-size: 1.5rem; color: #0066CC; font-weight: bold;">{triage_result['department']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            severity_color = {"High": "#DC3545", "Medium": "#FFC107", "Low": "#28A745"}.get(triage_result['severity'], "#0066CC")
            st.markdown(f"""
            <div class="info-card">
                <h3>⚠️ Severity Level</h3>
                <p style="font-size: 1.5rem; color: {severity_color}; font-weight: bold;">{triage_result['severity']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Recommended Doctors
        st.markdown("### 👨‍⚕️ Recommended Doctors")
        doctor_map = {d["name"]: d["id"] for d in triage_result["recommended_doctors"]}
        
        for doc_name in doctor_map.keys():
            st.markdown(f"""
            <div style="background: #F0F8FF; padding: 1rem; border-radius: 5px; margin: 0.5rem 0; border-left: 4px solid #00A86B;">
                👨‍⚕️ <strong>{doc_name}</strong> - {triage_result['department']} Specialist
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Booking Section
        st.markdown("""
        <div style="background: linear-gradient(90deg, #0066CC 0%, #00A86B 100%); padding: 1rem; border-radius: 8px; margin: 1rem 0;">
            <h2 style="color: white; margin: 0; text-align: center;">📅 Book Your Appointment</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            doctor_choice = st.selectbox("👨‍⚕️ Select Doctor", list(doctor_map.keys()), key="doctor_select")
        
        with col2:
            slot_options = triage_result["available_slots"]
            slot_labels = [datetime.fromisoformat(s).strftime("%d %B %Y, %I:%M %p") for s in slot_options]
            slot_choice = st.selectbox("🗓️ Choose Appointment Slot", slot_labels, key="slot_select")
        
        st.info("💡 **Tip:** Please arrive 10-15 minutes before your scheduled appointment time.")
        
        if st.button("✅ Confirm Booking", use_container_width=True, type="primary"):
            with st.spinner("📝 Booking your appointment..."):
                try:
                    payload = {
                        "patient_id": triage_result["patient_id"],
                        "doctor_id": doctor_map[doctor_choice],
                        "department_id": triage_result["department_id"],
                        "appointment_datetime": slot_options[slot_labels.index(slot_choice)],
                        "symptoms": st.session_state.get("last_symptoms") or "N/A",
                        "severity": triage_result["severity"],
                    }
                    booking = post_json("/api/patient/appointments", payload)
                    
                    # Success Message with Appointment Details
                    st.balloons()
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #28A745 0%, #20C997 100%); padding: 2rem; border-radius: 10px; color: white; margin: 1rem 0;">
                        <h2 style="text-align: center; margin: 0;">🎉 Appointment Confirmed Successfully!</h2>
                        <div style="background: rgba(255,255,255,0.2); padding: 1.5rem; border-radius: 8px; margin-top: 1rem;">
                            <p style="font-size: 1.2rem; margin: 0.5rem 0;"><strong>📋 Booking ID:</strong> {booking['id']}</p>
                            <p style="font-size: 1.2rem; margin: 0.5rem 0;"><strong>👨‍⚕️ Doctor:</strong> {booking['doctor_name']}</p>
                            <p style="font-size: 1.2rem; margin: 0.5rem 0;"><strong>🗓️ Date & Time:</strong> {booking['appointment_datetime']}</p>
                            <p style="font-size: 1.2rem; margin: 0.5rem 0;"><strong>🏥 Department:</strong> {booking['department_name']}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if booking.get('email_sent'):
                        st.success("📧 **Confirmation email sent** to your registered email address. Please check your inbox.")
                    else:
                        st.warning("⚠️ **Email notification could not be sent.** Please save your Booking ID for reference.")
                    
                    st.info("📌 **Important:** Please bring your Booking ID and a valid ID card when you visit the hospital.")
                    
                except Exception as exc:
                    st.error(f"❌ Booking Failed: {str(exc)}")

if role == "Admin":
    # Admin Dashboard Header - Compact
    st.markdown("""
    <div style="background: linear-gradient(135deg, #6C757D 0%, #343A40 100%); padding: 0.6rem; border-radius: 6px; margin: 0.5rem 0;">
        <h3 style="color: white; margin: 0; text-align: center; font-size: 1.2rem;">🔐 Admin Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    admin_password = st.text_input("Admin Password", type="password", placeholder="Enter Admin123")
    
    if admin_password:
        # Store in session for repeated use
        st.session_state["admin_password"] = admin_password
        headers = {"X-Admin-Password": admin_password}
        
        # === APPOINTMENTS MANAGEMENT ===
        st.subheader("📅 Appointments Management")
        
        col1, col2 = st.columns(2)
        with col1:
            load_appointments = st.button("🔄 Load All Appointments", use_container_width=True)
        with col2:
            if st.button("📊 Export to CSV", use_container_width=True):
                st.info("CSV export feature coming soon!")
        
        if load_appointments or st.session_state.get("appointments_loaded"):
            try:
                appointments = get_json("/api/admin/appointments", headers=headers)
                st.session_state["appointments_loaded"] = True
                st.session_state["appointments"] = appointments
                
                if appointments:
                    # Create filters
                    st.markdown("### 🔍 Filter Appointments")
                    filter_col1, filter_col2, filter_col3 = st.columns(3)
                    
                    # Extract unique values for filters
                    all_doctors = sorted(list(set([apt["doctor_name"] for apt in appointments])))
                    all_departments = sorted(list(set([apt["department_name"] for apt in appointments])))
                    all_dates = sorted(list(set([apt["appointment_datetime"][:10] for apt in appointments])))
                    
                    with filter_col1:
                        filter_doctor = st.selectbox("Filter by Doctor", ["All"] + all_doctors)
                    with filter_col2:
                        filter_department = st.selectbox("Filter by Department", ["All"] + all_departments)
                    with filter_col3:
                        filter_date = st.selectbox("Filter by Date", ["All"] + all_dates)
                    
                    # Apply filters
                    filtered_appointments = appointments
                    if filter_doctor != "All":
                        filtered_appointments = [apt for apt in filtered_appointments if apt["doctor_name"] == filter_doctor]
                    if filter_department != "All":
                        filtered_appointments = [apt for apt in filtered_appointments if apt["department_name"] == filter_department]
                    if filter_date != "All":
                        filtered_appointments = [apt for apt in filtered_appointments if apt["appointment_datetime"][:10] == filter_date]
                    
                    # Display count
                    st.info(f"📊 Showing {len(filtered_appointments)} of {len(appointments)} appointments")
                    
                    # Display as table
                    if filtered_appointments:
                        import pandas as pd
                        df = pd.DataFrame(filtered_appointments)
                        
                        # Reorder columns for better display
                        column_order = ["id", "appointment_datetime", "patient_name", "doctor_name", 
                                      "department_name", "severity", "symptoms", "email_sent"]
                        df = df[[col for col in column_order if col in df.columns]]
                        
                        # Rename columns for better readability
                        df.columns = ["Booking ID", "Date & Time", "Patient", "Doctor", 
                                     "Department", "Severity", "Symptoms", "Email Sent"]
                        
                        # Style the dataframe
                        st.dataframe(
                            df,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Booking ID": st.column_config.NumberColumn("Booking ID", width="small"),
                                "Date & Time": st.column_config.DatetimeColumn("Date & Time", format="YYYY-MM-DD HH:mm"),
                                "Severity": st.column_config.TextColumn("Severity", width="small"),
                                "Email Sent": st.column_config.CheckboxColumn("Email Sent", width="small"),
                            }
                        )
                    else:
                        st.warning("⚠️ No appointments match the selected filters.")
                else:
                    st.info("ℹ️ No appointments found in the system.")
                    
            except Exception as exc:
                st.error(f"❌ Error loading appointments: {str(exc)}")
                st.session_state["appointments_loaded"] = False
        
        st.divider()
        
        # === DOCTOR UNAVAILABILITY MANAGEMENT ===
        st.subheader("🏥 Doctor Leave & Unavailability Management")
        
        tab1, tab2 = st.tabs(["📋 View Leave Records", "➕ Add Doctor Leave"])
        
        with tab1:
            if st.button("🔄 Refresh Leave Records", use_container_width=True):
                try:
                    leave_data = get_json("/api/admin/doctor-unavailable", headers=headers)
                    st.session_state["leave_records"] = leave_data
                except Exception as exc:
                    st.error(f"❌ Error: {str(exc)}")
            
            leave_records = st.session_state.get("leave_records")
            if leave_records:
                if leave_records:
                    import pandas as pd
                    df = pd.DataFrame(leave_records)
                    
                    # Enhance display - Simple table with doctor name
                    display_columns = ['id', 'doctor_name', 'date', 'reason']
                    df_display = df[[col for col in display_columns if col in df.columns]]
                    
                    st.dataframe(
                        df_display,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "id": st.column_config.NumberColumn("Leave ID", width="small"),
                            "doctor_name": st.column_config.TextColumn("Doctor Name", width="medium"),
                            "date": st.column_config.DateColumn("Leave Date", width="medium"),
                            "reason": st.column_config.TextColumn("Reason"),
                        }
                    )
                    
                    # Simple statistics
                    st.metric("📋 Total Leave Records", len(leave_records))
                else:
                    st.info("ℹ️ No leave records found.")
            else:
                st.info("👆 Click 'Refresh Leave Records' to view all doctor leaves")
        
        with tab2:
            st.markdown("### ➕ Add New Doctor Leave")
            
            # Fetch doctors list
            if st.button("👨‍⚕️ Load All Doctors", use_container_width=True):
                try:
                    doctors_data = get_json("/api/admin/doctors", headers=headers)
                    st.session_state["doctors_list"] = doctors_data
                except Exception as exc:
                    st.error(f"❌ Error loading doctors: {str(exc)}")
            
            doctors_list = st.session_state.get("doctors_list")
            
            if doctors_list:
                # Show doctors table
                st.markdown("#### 👨‍⚕️ Available Doctors")
                import pandas as pd
                doctors_df = pd.DataFrame(doctors_list)
                st.dataframe(
                    doctors_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "id": st.column_config.NumberColumn("ID", width="small"),
                        "name": st.column_config.TextColumn("Doctor Name"),
                        "department": st.column_config.TextColumn("Department"),
                        "email": st.column_config.TextColumn("Email"),
                        "is_active": st.column_config.CheckboxColumn("Active", width="small"),
                    }
                )
                
                st.divider()
                
                # Add leave form
                with st.form("add_leave_form"):
                    st.markdown("#### 📝 Enter Leave Details")
                    
                    # Create doctor selection dropdown
                    doctor_options = {f"{d['name']} (ID: {d['id']}) - {d['department']}": d['id'] for d in doctors_list}
                    selected_doctor = st.selectbox("👨‍⚕️ Select Doctor *", list(doctor_options.keys()))
                    doctor_id = doctor_options[selected_doctor]
                    
                    leave_date = st.date_input("🗓️ Leave Date *", key="leave_date")
                    leave_reason = st.text_area("📝 Reason *", placeholder="e.g., Medical Conference, Personal Leave, Vacation, Annual Leave", height=100)
                    
                    submit_leave = st.form_submit_button("✅ Add Leave Record", use_container_width=True, type="primary")
                    
                    if submit_leave:
                        if not leave_reason:
                            st.error("❌ Please provide a reason for leave")
                        else:
                            try:
                                payload = {
                                    "doctor_id": doctor_id,
                                    "date": leave_date.isoformat(),
                                    "reason": leave_reason
                                }
                                
                                import requests
                                response = requests.post(
                                    f"{API_BASE}/api/admin/doctor-unavailable",
                                    json=payload,
                                    headers=headers
                                )
                                
                                if response.status_code == 200:
                                    st.success(f"✅ Leave record added successfully!")
                                    st.info(f"🏥 **Doctor:** {selected_doctor.split(' (ID:')[0]}\n\n📅 **Date:** {leave_date}\n\n📝 **Reason:** {leave_reason}")
                                    st.balloons()
                                else:
                                    st.error(f"❌ Failed to add leave: {response.text}")
                            except Exception as exc:
                                st.error(f"❌ Error: {str(exc)}")
            else:
                st.info("👆 Click 'Load All Doctors' to see the list and add leave records")
        
        st.divider()
        
        # === STATISTICS ===
        st.subheader("📈 Quick Statistics")
        if st.session_state.get("appointments"):
            appointments = st.session_state["appointments"]
            
            stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
            
            with stat_col1:
                st.metric("Total Appointments", len(appointments))
            with stat_col2:
                high_severity = len([a for a in appointments if a.get("severity") == "High"])
                st.metric("High Severity", high_severity, delta="Urgent" if high_severity > 0 else None)
            with stat_col3:
                emails_sent = len([a for a in appointments if a.get("email_sent")])
                st.metric("Emails Sent", emails_sent)
            with stat_col4:
                unique_patients = len(set([a["patient_name"] for a in appointments]))
                st.metric("Unique Patients", unique_patients)
    
    else:
        st.warning("⚠️ Please enter admin password to access dashboard")

# Footer with Hospital Information - Compact
st.divider()
st.markdown("""
<div style="background: linear-gradient(135deg, #0066CC 0%, #00A86B 100%); padding: 1rem; border-radius: 6px; margin-top: 1rem; color: white;">
    <div style="text-align: center;">
        <div style="display: flex; justify-content: center; gap: 1.5rem; flex-wrap: wrap; font-size: 0.85rem;">
            <div>📞 Emergency: +1-800-GETLIFE</div>
            <div>📧 info@getlifehospital.com</div>
            <div>🕒 24/7 Emergency Services</div>
        </div>
        <p style="margin-top: 0.5rem; font-size: 0.75rem; opacity: 0.9;">
            © 2025 Get Life Hospital - Advanced Healthcare Services
        </p>
    </div>
</div>
""", unsafe_allow_html=True)


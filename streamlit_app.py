# Job Search CRM - Enhanced Streamlit Version
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# File-based storage
APPLICATIONS_FILE = "applications.csv"
COMPANIES_FILE = "companies.csv"
NETWORKING_FILE = "networking.csv" 
INTERVIEWS_FILE = "interviews.csv"

def load_applications():
    """Load applications from CSV file"""
    if os.path.exists(APPLICATIONS_FILE):
        return pd.read_csv(APPLICATIONS_FILE)
    else:
        return pd.DataFrame(columns=[
            'date_applied', 'company', 'role_title', 'job_link', 'status', 
            'priority', 'salary_range', 'location', 'next_action', 
            'follow_up_date', 'notes'
        ])

def save_applications(df):
    """Save applications to CSV file"""
    df.to_csv(APPLICATIONS_FILE, index=False)

def load_companies():
    """Load companies from CSV file"""
    if os.path.exists(COMPANIES_FILE):
        return pd.read_csv(COMPANIES_FILE)
    else:
        return pd.DataFrame(columns=[
            'company', 'industry', 'size', 'tech_stack', 'culture_notes', 
            'glassdoor_rating', 'key_contacts', 'open_roles', 'applied_status'
        ])

def save_companies(df):
    """Save companies to CSV file"""
    df.to_csv(COMPANIES_FILE, index=False)

def load_networking():
    """Load networking from CSV file"""
    if os.path.exists(NETWORKING_FILE):
        return pd.read_csv(NETWORKING_FILE)
    else:
        return pd.DataFrame(columns=[
            'contact_name', 'company', 'position', 'connection_type', 
            'contact_date', 'response', 'meeting_scheduled', 
            'follow_up_action', 'notes'
        ])

def save_networking(df):
    """Save networking to CSV file"""
    df.to_csv(NETWORKING_FILE, index=False)

def load_interviews():
    """Load interviews from CSV file"""
    if os.path.exists(INTERVIEWS_FILE):
        return pd.read_csv(INTERVIEWS_FILE)
    else:
        return pd.DataFrame(columns=[
            'company', 'interview_date', 'interview_type', 'interviewer', 
            'prep_status', 'key_topics', 'questions_to_ask', 'outcome', 'next_steps'
        ])

def save_interviews(df):
    """Save interviews to CSV file"""
    df.to_csv(INTERVIEWS_FILE, index=False)

def display_data_with_actions(df, save_function, data_type, column_configs=None):
    """Display data with edit/delete actions for each row"""
    if df.empty:
        st.info(f"No {data_type.lower()} data yet. Add some using the form above!")
        return df
    
    st.subheader(f"All {data_type} ({len(df)})")
    
    # Create action buttons for each row
    for idx, row in df.iterrows():
        with st.container():
            # Display row data in expandable format
            if data_type == "Applications":
                row_title = f"{row['company']} - {row['role_title']} ({row['status']})"
            elif data_type == "Companies":
                row_title = f"{row['company']} - {row['industry']} ({row['applied_status']})"
            elif data_type == "Contacts":
                row_title = f"{row['contact_name']} ({row['company']}) - {row['response']}"
            elif data_type == "Interviews":
                row_title = f"{row['company']} - {row['interview_type']} ({row['prep_status']})"
            else:
                row_title = f"Row {idx + 1}"
            
            with st.expander(f"📝 {row_title}"):
                col1, col2, col3 = st.columns([6, 1, 1])
                
                # Display row details in main column
                with col1:
                    row_data = {}
                    for col in df.columns:
                        if pd.notna(row[col]) and str(row[col]).strip():
                            row_data[col.replace('_', ' ').title()] = str(row[col])
                    
                    # Display in a nice format
                    for key, value in row_data.items():
                        if key == 'Job Link' and value.startswith('http'):
                            st.markdown(f"**{key}:** [{value}]({value})")
                        else:
                            st.write(f"**{key}:** {value}")
                
                # Edit button
                with col2:
                    if st.button("✏️", key=f"edit_{data_type}_{idx}", help="Edit this entry"):
                        st.session_state[f'editing_{data_type}_{idx}'] = True
                        st.rerun()
                
                # Delete button
                with col3:
                    if st.button("🗑️", key=f"delete_{data_type}_{idx}", help="Delete this entry", type="secondary"):
                        # Confirm deletion
                        if st.button(f"⚠️ Confirm Delete", key=f"confirm_delete_{data_type}_{idx}", type="secondary"):
                            df_updated = df.drop(idx).reset_index(drop=True)
                            save_function(df_updated)
                            st.success(f"✅ Deleted entry")
                            st.rerun()
                        else:
                            st.warning("Click 'Confirm Delete' to permanently delete this entry")
                
                # Edit form (appears when edit button is clicked)
                if st.session_state.get(f'editing_{data_type}_{idx}', False):
                    st.markdown("---")
                    st.subheader("Edit Entry")
                    
                    with st.form(f"edit_form_{data_type}_{idx}"):
                        edited_data = {}
                        
                        if data_type == "Applications":
                            col1, col2 = st.columns(2)
                            with col1:
                                edited_data['date_applied'] = st.date_input("Date Applied", value=pd.to_datetime(row['date_applied']).date() if pd.notna(row['date_applied']) else datetime.now().date())
                                edited_data['company'] = st.text_input("Company", value=str(row['company']) if pd.notna(row['company']) else "")
                                edited_data['role_title'] = st.text_input("Role Title", value=str(row['role_title']) if pd.notna(row['role_title']) else "")
                                edited_data['job_link'] = st.text_input("Job Link", value=str(row['job_link']) if pd.notna(row['job_link']) else "")
                                edited_data['status'] = st.selectbox("Status", ["Applied", "Interview", "Rejected", "Offer", "Follow-up"], 
                                                                   index=["Applied", "Interview", "Rejected", "Offer", "Follow-up"].index(row['status']) if pd.notna(row['status']) and row['status'] in ["Applied", "Interview", "Rejected", "Offer", "Follow-up"] else 0)
                            with col2:
                                edited_data['priority'] = st.selectbox("Priority", ["High", "Medium", "Low"], 
                                                                     index=["High", "Medium", "Low"].index(row['priority']) if pd.notna(row['priority']) and row['priority'] in ["High", "Medium", "Low"] else 1)
                                edited_data['salary_range'] = st.text_input("Salary Range", value=str(row['salary_range']) if pd.notna(row['salary_range']) else "")
                                edited_data['location'] = st.text_input("Location", value=str(row['location']) if pd.notna(row['location']) else "")
                                edited_data['next_action'] = st.text_input("Next Action", value=str(row['next_action']) if pd.notna(row['next_action']) else "")
                                edited_data['follow_up_date'] = st.date_input("Follow-up Date", value=pd.to_datetime(row['follow_up_date']).date() if pd.notna(row['follow_up_date']) else None)
                            edited_data['notes'] = st.text_area("Notes", value=str(row['notes']) if pd.notna(row['notes']) else "")
                        
                        elif data_type == "Companies":
                            col1, col2 = st.columns(2)
                            with col1:
                                edited_data['company'] = st.text_input("Company", value=str(row['company']) if pd.notna(row['company']) else "")
                                edited_data['industry'] = st.text_input("Industry", value=str(row['industry']) if pd.notna(row['industry']) else "")
                                edited_data['size'] = st.selectbox("Company Size", ["<50", "50-200", "200-1000", "1000-5000", "5000+", "10,000+"],
                                                                 index=["<50", "50-200", "200-1000", "1000-5000", "5000+", "10,000+"].index(row['size']) if pd.notna(row['size']) and row['size'] in ["<50", "50-200", "200-1000", "1000-5000", "5000+", "10,000+"] else 0)
                                edited_data['tech_stack'] = st.text_input("Tech Stack", value=str(row['tech_stack']) if pd.notna(row['tech_stack']) else "")
                            with col2:
                                edited_data['culture_notes'] = st.text_input("Culture Notes", value=str(row['culture_notes']) if pd.notna(row['culture_notes']) else "")
                                edited_data['glassdoor_rating'] = st.selectbox("Glassdoor Rating", ["1.0/5", "1.5/5", "2.0/5", "2.5/5", "3.0/5", "3.5/5", "4.0/5", "4.5/5", "5.0/5"],
                                                                             index=["1.0/5", "1.5/5", "2.0/5", "2.5/5", "3.0/5", "3.5/5", "4.0/5", "4.5/5", "5.0/5"].index(row['glassdoor_rating']) if pd.notna(row['glassdoor_rating']) and row['glassdoor_rating'] in ["1.0/5", "1.5/5", "2.0/5", "2.5/5", "3.0/5", "3.5/5", "4.0/5", "4.5/5", "5.0/5"] else 4)
                                edited_data['key_contacts'] = st.text_input("Key Contacts", value=str(row['key_contacts']) if pd.notna(row['key_contacts']) else "")
                                edited_data['open_roles'] = st.text_input("Open Roles", value=str(row['open_roles']) if pd.notna(row['open_roles']) else "")
                            edited_data['applied_status'] = st.selectbox("Applied Status", ["❌ Not yet", "🎯 Target", "✅ Applied"],
                                                                       index=["❌ Not yet", "🎯 Target", "✅ Applied"].index(row['applied_status']) if pd.notna(row['applied_status']) and row['applied_status'] in ["❌ Not yet", "🎯 Target", "✅ Applied"] else 0)
                        
                        elif data_type == "Contacts":
                            col1, col2 = st.columns(2)
                            with col1:
                                edited_data['contact_name'] = st.text_input("Contact Name", value=str(row['contact_name']) if pd.notna(row['contact_name']) else "")
                                edited_data['company'] = st.text_input("Company", value=str(row['company']) if pd.notna(row['company']) else "")
                                edited_data['position'] = st.text_input("Position", value=str(row['position']) if pd.notna(row['position']) else "")
                                edited_data['connection_type'] = st.selectbox("Connection Type", ["LinkedIn", "NTNU Alumni", "Referral", "Cold Outreach", "Meetup", "Conference"],
                                                                            index=["LinkedIn", "NTNU Alumni", "Referral", "Cold Outreach", "Meetup", "Conference"].index(row['connection_type']) if pd.notna(row['connection_type']) and row['connection_type'] in ["LinkedIn", "NTNU Alumni", "Referral", "Cold Outreach", "Meetup", "Conference"] else 0)
                            with col2:
                                edited_data['contact_date'] = st.date_input("Contact Date", value=pd.to_datetime(row['contact_date']).date() if pd.notna(row['contact_date']) else datetime.now().date())
                                edited_data['response'] = st.selectbox("Response", ["✅ Responded", "❌ No response", "🔄 Pending"],
                                                                      index=["✅ Responded", "❌ No response", "🔄 Pending"].index(row['response']) if pd.notna(row['response']) and row['response'] in ["✅ Responded", "❌ No response", "🔄 Pending"] else 2)
                                edited_data['meeting_scheduled'] = st.text_input("Meeting Scheduled", value=str(row['meeting_scheduled']) if pd.notna(row['meeting_scheduled']) else "")
                                edited_data['follow_up_action'] = st.text_input("Follow-up Action", value=str(row['follow_up_action']) if pd.notna(row['follow_up_action']) else "")
                            edited_data['notes'] = st.text_area("Notes", value=str(row['notes']) if pd.notna(row['notes']) else "")
                        
                        elif data_type == "Interviews":
                            col1, col2 = st.columns(2)
                            with col1:
                                edited_data['company'] = st.text_input("Company", value=str(row['company']) if pd.notna(row['company']) else "")
                                edited_data['interview_date'] = st.text_input("Interview Date & Time", value=str(row['interview_date']) if pd.notna(row['interview_date']) else "")
                                edited_data['interview_type'] = st.selectbox("Interview Type", ["1st Round - HR", "2nd Round - Technical", "3rd Round - Manager", "Final Round", "Case Study", "Panel Interview"],
                                                                            index=["1st Round - HR", "2nd Round - Technical", "3rd Round - Manager", "Final Round", "Case Study", "Panel Interview"].index(row['interview_type']) if pd.notna(row['interview_type']) and row['interview_type'] in ["1st Round - HR", "2nd Round - Technical", "3rd Round - Manager", "Final Round", "Case Study", "Panel Interview"] else 0)
                                edited_data['interviewer'] = st.text_input("Interviewer(s)", value=str(row['interviewer']) if pd.notna(row['interviewer']) else "")
                            with col2:
                                edited_data['prep_status'] = st.selectbox("Prep Status", ["✅ Ready", "🔄 In progress", "❌ Need work"],
                                                                         index=["✅ Ready", "🔄 In progress", "❌ Need work"].index(row['prep_status']) if pd.notna(row['prep_status']) and row['prep_status'] in ["✅ Ready", "🔄 In progress", "❌ Need work"] else 1)
                                edited_data['key_topics'] = st.text_input("Key Topics to Cover", value=str(row['key_topics']) if pd.notna(row['key_topics']) else "")
                                edited_data['questions_to_ask'] = st.text_input("Questions to Ask", value=str(row['questions_to_ask']) if pd.notna(row['questions_to_ask']) else "")
                                edited_data['outcome'] = st.selectbox("Outcome", ["", "Positive", "Neutral", "Negative"],
                                                                     index=["", "Positive", "Neutral", "Negative"].index(row['outcome']) if pd.notna(row['outcome']) and row['outcome'] in ["", "Positive", "Neutral", "Negative"] else 0)
                            edited_data['next_steps'] = st.text_area("Next Steps", value=str(row['next_steps']) if pd.notna(row['next_steps']) else "")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("💾 Save Changes", type="primary"):
                                # Update the dataframe
                                for key, value in edited_data.items():
                                    df.loc[idx, key] = value
                                save_function(df)
                                st.session_state[f'editing_{data_type}_{idx}'] = False
                                st.success("✅ Changes saved successfully!")
                                st.rerun()
                        
                        with col2:
                            if st.form_submit_button("❌ Cancel"):
                                st.session_state[f'editing_{data_type}_{idx}'] = False
                                st.rerun()
    
    return df

# Streamlit App Configuration
st.set_page_config(
    page_title="Job Search CRM", 
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎯 Job Search CRM")
st.markdown("Track your applications, networking, and progress")

# Initialize session state for editing
if 'editing_states' not in st.session_state:
    st.session_state.editing_states = {}

# Sidebar navigation
st.sidebar.header("Navigation")
page = st.sidebar.selectbox(
    "Choose Section", 
    ["📊 Dashboard", "📋 Applications", "🏢 Companies", "🤝 Networking", "📝 Interviews"]
)

# Dashboard 
if page == "📊 Dashboard":
    st.header("📊 Dashboard")
    
    # Load all data for metrics
    applications_df = load_applications()
    companies_df = load_companies()
    networking_df = load_networking()
    interviews_df = load_interviews()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_apps = len(applications_df)
        st.metric("Total Applications", total_apps)
    
    with col2:
        interviews_count = len(applications_df[applications_df['status'] == 'Interview']) if 'status' in applications_df.columns else 0
        st.metric("Interviews", interviews_count)
    
    with col3:
        if total_apps > 0:
            offers = len(applications_df[applications_df['status'] == 'Offer']) if 'status' in applications_df.columns else 0
            response_rate = round(((interviews_count + offers) / total_apps) * 100, 1)
            st.metric("Response Rate", f"{response_rate}%")
        else:
            st.metric("Response Rate", "0%")
    
    with col4:
        offers_count = len(applications_df[applications_df['status'] == 'Offer']) if 'status' in applications_df.columns else 0
        st.metric("Offers", offers_count)
    
    if not applications_df.empty:
        st.subheader("Application Status Distribution")
        status_counts = applications_df['status'].value_counts()
        st.bar_chart(status_counts)
        
        st.subheader("Recent Applications")
        recent_apps = applications_df.sort_values('date_applied', ascending=False).head(5)
        st.dataframe(recent_apps, use_container_width=True)
    else:
        st.info("📝 No applications yet. Start by adding some in the Applications tab!")

# Applications
elif page == "📋 Applications":
    st.header("📋 Job Applications")
    
    applications_df = load_applications()
    
    # Add new application form
    with st.expander("➕ Add New Application", expanded=True):
        with st.form("new_application"):
            col1, col2 = st.columns(2)
            
            with col1:
                date_applied = st.date_input("Date Applied", value=datetime.now())
                company = st.text_input("Company *", placeholder="e.g., Cathay Financial")
                role_title = st.text_input("Role Title *", placeholder="e.g., Data Analyst") 
                job_link = st.text_input("Job Link", placeholder="https://104.com.tw/job/...")
                status = st.selectbox("Status", ["Applied", "Interview", "Rejected", "Offer", "Follow-up"])
            
            with col2:
                priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                salary_range = st.text_input("Salary Range", placeholder="NT$800K-1.2M")
                location = st.text_input("Location", placeholder="Taipei, Remote, Hybrid")
                next_action = st.text_input("Next Action", placeholder="Follow up, Prepare interview")
                follow_up_date = st.date_input("Follow-up Date", value=None)
            
            notes = st.text_area("Notes", placeholder="Requirements, contact info, etc.")
            
            if st.form_submit_button("💾 Save Application", type="primary"):
                if company and role_title:
                    new_row = pd.DataFrame({
                        'date_applied': [date_applied],
                        'company': [company],
                        'role_title': [role_title],
                        'job_link': [job_link],
                        'status': [status],
                        'priority': [priority],
                        'salary_range': [salary_range],
                        'location': [location],
                        'next_action': [next_action],
                        'follow_up_date': [follow_up_date],
                        'notes': [notes]
                    })
                    
                    applications_df = pd.concat([applications_df, new_row], ignore_index=True)
                    save_applications(applications_df)
                    st.success(f"✅ Added application for {role_title} at {company}")
                    st.rerun()
                else:
                    st.error("❌ Please fill in Company and Role Title fields")
    
    # Display applications with actions
    applications_df = display_data_with_actions(applications_df, save_applications, "Applications")
    
    # Download button
    if not applications_df.empty:
        st.download_button(
            label="📥 Download Applications CSV",
            data=applications_df.to_csv(index=False),
            file_name=f"applications_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# Companies  
elif page == "🏢 Companies":
    st.header("🏢 Company Research")
    
    companies_df = load_companies()
    
    # Add new company form
    with st.expander("➕ Add Company Research", expanded=True):
        with st.form("new_company"):
            col1, col2 = st.columns(2)
            
            with col1:
                company = st.text_input("Company *", placeholder="e.g., Cathay Financial")
                industry = st.text_input("Industry", placeholder="e.g., Fintech/Banking")
                size = st.selectbox("Company Size", ["<50", "50-200", "200-1000", "1000-5000", "5000+", "10,000+"])
                tech_stack = st.text_input("Tech Stack", placeholder="SQL, Tableau, Python")
            
            with col2:
                culture_notes = st.text_input("Culture Notes", placeholder="Traditional, fast-paced, etc.")
                glassdoor_rating = st.selectbox("Glassdoor Rating", ["1.0/5", "1.5/5", "2.0/5", "2.5/5", "3.0/5", "3.5/5", "4.0/5", "4.5/5", "5.0/5"])
                key_contacts = st.text_input("Key Contacts", placeholder="Name (Position)")
                open_roles = st.text_input("Open Roles", placeholder="Data Analyst, BI Developer")
            
            applied_status = st.selectbox("Applied Status", ["❌ Not yet", "🎯 Target", "✅ Applied"])
            
            if st.form_submit_button("💾 Save Company", type="primary"):
                if company:
                    new_row = pd.DataFrame({
                        'company': [company],
                        'industry': [industry],
                        'size': [size],
                        'tech_stack': [tech_stack],
                        'culture_notes': [culture_notes],
                        'glassdoor_rating': [glassdoor_rating],
                        'key_contacts': [key_contacts],
                        'open_roles': [open_roles],
                        'applied_status': [applied_status]
                    })
                    
                    companies_df = pd.concat([companies_df, new_row], ignore_index=True)
                    save_companies(companies_df)
                    st.success(f"✅ Added {company} to research")
                    st.rerun()
                else:
                    st.error("❌ Please fill in Company name")
    
    # Display companies with actions
    companies_df = display_data_with_actions(companies_df, save_companies, "Companies")
    
    # Download button
    if not companies_df.empty:
        st.download_button(
            label="📥 Download Companies CSV",
            data=companies_df.to_csv(index=False),
            file_name=f"companies_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# Networking
elif page == "🤝 Networking":
    st.header("🤝 Networking Tracker")
    
    networking_df = load_networking()
    
    # Add new contact form
    with st.expander("➕ Add New Contact", expanded=True):
        with st.form("new_contact"):
            col1, col2 = st.columns(2)
            
            with col1:
                contact_name = st.text_input("Contact Name *", placeholder="e.g., Sarah Chen")
                company = st.text_input("Company", placeholder="e.g., PChome")
                position = st.text_input("Position", placeholder="e.g., Senior Data Analyst")
                connection_type = st.selectbox("Connection Type", ["LinkedIn", "NTNU Alumni", "Referral", "Cold Outreach", "Meetup", "Conference"])
            
            with col2:
                contact_date = st.date_input("Contact Date", value=datetime.now())
                response = st.selectbox("Response", ["✅ Responded", "❌ No response", "🔄 Pending"])
                meeting_scheduled = st.text_input("Meeting Scheduled", placeholder="2025-08-21 10:00 AM")
                follow_up_action = st.text_input("Follow-up Action", placeholder="Send thank you, Ask for referral")
            
            notes = st.text_area("Notes", placeholder="Details about the conversation, next steps, etc.")
            
            if st.form_submit_button("💾 Save Contact", type="primary"):
                if contact_name:
                    new_row = pd.DataFrame({
                        'contact_name': [contact_name],
                        'company': [company],
                        'position': [position],
                        'connection_type': [connection_type],
                        'contact_date': [contact_date],
                        'response': [response],
                        'meeting_scheduled': [meeting_scheduled],
                        'follow_up_action': [follow_up_action],
                        'notes': [notes]
                    })
                    
                    networking_df = pd.concat([networking_df, new_row], ignore_index=True)
                    save_networking(networking_df)
                    st.success(f"✅ Added contact {contact_name}")
                    st.rerun()
                else:
                    st.error("❌ Please fill in Contact Name")
    
    # Display networking with actions
    networking_df = display_data_with_actions(networking_df, save_networking, "Contacts")
    
    # Download button
    if not networking_df.empty:
        st.download_button(
            label="📥 Download Networking CSV",
            data=networking_df.to_csv(index=False),
            file_name=f"networking_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

# Interviews
elif page == "📝 Interviews":
    st.header("📝 Interview Preparation")
    
    interviews_df = load_interviews()
    
    # Add new interview form
    with st.expander("➕ Add New Interview", expanded=True):
        with st.form("new_interview"):
            col1, col2 = st.columns(2)
            
            with col1:
                company = st.text_input("Company *", placeholder="e.g., PChome")
                interview_date = st.text_input("Interview Date & Time", placeholder="2025-08-22 2:00 PM")
                interview_type = st.selectbox("Interview Type", ["1st Round - HR", "2nd Round - Technical", "3rd Round - Manager", "Final Round", "Case Study", "Panel Interview"])
                interviewer = st.text_input("Interviewer(s)", placeholder="e.g., Jennifer Liu, David Chang")
            
            with col2:
                prep_status = st.selectbox("Prep Status", ["✅ Ready", "🔄 In progress", "❌ Need work"])
                key_topics = st.text_input("Key Topics to Cover", placeholder="SQL skills, project examples, culture fit")
                questions_to_ask = st.text_input("Questions to Ask", placeholder="Team structure, growth opportunities")
                outcome = st.selectbox("Outcome", ["", "Positive", "Neutral", "Negative"])
            
            next_steps = st.text_area("Next Steps", placeholder="2nd round scheduled, waiting for feedback, etc.")
            
            if st.form_submit_button("💾 Save Interview", type="primary"):
                if company:
                    new_row = pd.DataFrame({
                        'company': [company],
                        'interview_date': [interview_date],
                        'interview_type': [interview_type],
                        'interviewer': [interviewer],
                        'prep_status': [prep_status],
                        'key_topics': [key_topics],
                        'questions_to_ask': [questions_to_ask],
                        'outcome': [outcome],
                        'next_steps': [next_steps]
                    })
                    
                    interviews_df = pd.concat([interviews_df, new_row], ignore_index=True)
                    save_interviews(interviews_df)
                    st.success(f"✅ Added interview for {company}")
                    st.rerun()
                else:
                    st.error("❌ Please fill in Company name")
    
    # Display interviews with actions
    interviews_df = display_data_with_actions(interviews_df, save_interviews, "Interviews")
    
    # Download button
    if not interviews_df.empty:
        st.download_button(
            label="📥 Download Interviews CSV",
            data=interviews_df.to_csv(index=False),
            file_name=f"interviews_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

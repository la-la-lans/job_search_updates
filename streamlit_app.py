# Job Search CRM - Streamlit Version
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
            'date_applied', 'company', 'role_title', 'job_board', 'status', 
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

def delete_rows_interface(df, save_function, item_name):
    """Generic delete interface for any dataframe"""
    if not df.empty and st.checkbox(f"🗑️ Enable Delete Mode for {item_name}"):
        st.warning("⚠️ Delete mode enabled")
        
        # Create display names for selection
        if 'company' in df.columns and 'role_title' in df.columns:
            display_names = [f"{row['company']} - {row['role_title']}" for _, row in df.iterrows()]
        elif 'company' in df.columns and 'contact_name' in df.columns:
            display_names = [f"{row['contact_name']} ({row['company']})" for _, row in df.iterrows()]
        elif 'company' in df.columns:
            display_names = [f"{row['company']}" for _, row in df.iterrows()]
        else:
            display_names = [f"Row {i+1}" for i in range(len(df))]
        
        selected_indices = st.multiselect(
            f"Select {item_name.lower()} to delete:",
            range(len(df)),
            format_func=lambda x: display_names[x]
        )
        
        if selected_indices and st.button(f"🗑️ Delete Selected {item_name}", type="secondary"):
            df_updated = df.drop(selected_indices).reset_index(drop=True)
            save_function(df_updated)
            st.success(f"✅ Deleted {len(selected_indices)} {item_name.lower()}")
            st.rerun()
            return df_updated
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
                job_board = st.selectbox("Job Board", ["104.com.tw", "LinkedIn", "CakeResume", "Yourator", "Company Direct"])
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
                        'job_board': [job_board],
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
    
    # Display applications table
    if not applications_df.empty:
        st.subheader(f"All Applications ({len(applications_df)})")
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.multiselect(
                "Filter by Status", 
                applications_df['status'].unique(),
                default=applications_df['status'].unique()
            )
        with col2:
            priority_filter = st.multiselect(
                "Filter by Priority", 
                applications_df['priority'].unique(),
                default=applications_df['priority'].unique()
            )
        
        # Apply filters
        filtered_df = applications_df[
            (applications_df['status'].isin(status_filter)) &
            (applications_df['priority'].isin(priority_filter))
        ]
        
        # Display table
        st.dataframe(
            filtered_df,
            use_container_width=True,
            column_config={
                "date_applied": st.column_config.DateColumn("Date Applied"),
                "company": st.column_config.TextColumn("Company", width="medium"),
                "role_title": st.column_config.TextColumn("Role Title", width="medium"),
                "job_board": st.column_config.TextColumn("Job Board"),
                "status": st.column_config.TextColumn("Status"),
                "priority": st.column_config.TextColumn("Priority"),
                "salary_range": st.column_config.TextColumn("Salary Range"),
                "location": st.column_config.TextColumn("Location"),
                "next_action": st.column_config.TextColumn("Next Action"),
                "follow_up_date": st.column_config.DateColumn("Follow-up Date"),
                "notes": st.column_config.TextColumn("Notes", width="large")
            }
        )
        
        # Delete interface
        applications_df = delete_rows_interface(applications_df, save_applications, "Applications")
        
        # Download button
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
    
    # Display companies table
    if not companies_df.empty:
        st.subheader(f"Company Research ({len(companies_df)})")
        
        st.dataframe(
            companies_df,
            use_container_width=True,
            column_config={
                "company": st.column_config.TextColumn("Company", width="medium"),
                "industry": st.column_config.TextColumn("Industry"),
                "size": st.column_config.TextColumn("Size"),
                "tech_stack": st.column_config.TextColumn("Tech Stack", width="medium"),
                "culture_notes": st.column_config.TextColumn("Culture Notes", width="medium"),
                "glassdoor_rating": st.column_config.TextColumn("Rating"),
                "key_contacts": st.column_config.TextColumn("Key Contacts", width="medium"),
                "open_roles": st.column_config.TextColumn("Open Roles", width="medium"),
                "applied_status": st.column_config.TextColumn("Applied?")
            }
        )
        
        # Delete interface
        companies_df = delete_rows_interface(companies_df, save_companies, "Companies")
        
        # Download button
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
    
    # Display networking table
    if not networking_df.empty:
        st.subheader(f"Networking Contacts ({len(networking_df)})")
        
        st.dataframe(
            networking_df,
            use_container_width=True,
            column_config={
                "contact_name": st.column_config.TextColumn("Contact Name", width="medium"),
                "company": st.column_config.TextColumn("Company"),
                "position": st.column_config.TextColumn("Position", width="medium"),
                "connection_type": st.column_config.TextColumn("Connection Type"),
                "contact_date": st.column_config.DateColumn("Contact Date"),
                "response": st.column_config.TextColumn("Response"),
                "meeting_scheduled": st.column_config.TextColumn("Meeting Scheduled"),
                "follow_up_action": st.column_config.TextColumn("Follow-up Action", width="medium"),
                "notes": st.column_config.TextColumn("Notes", width="large")
            }
        )
        
        # Delete interface
        networking_df = delete_rows_interface(networking_df, save_networking, "Contacts")
        
        # Download button
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
    
    # Display interviews table
    if not interviews_df.empty:
        st.subheader(f"Interview Schedule ({len(interviews_df)})")
        
        st.dataframe(
            interviews_df,
            use_container_width=True,
            column_config={
                "company": st.column_config.TextColumn("Company", width="medium"),
                "interview_date": st.column_config.TextColumn("Date & Time", width="medium"),
                "interview_type": st.column_config.TextColumn("Type"),
                "interviewer": st.column_config.TextColumn("Interviewer(s)", width="medium"),
                "prep_status": st.column_config.TextColumn("Prep Status"),
                "key_topics": st.column_config.TextColumn("Key Topics", width="large"),
                "questions_to_ask": st.column_config.TextColumn("Questions to Ask", width="large"),
                "outcome": st.column_config.TextColumn("Outcome"),
                "next_steps": st.column_config.TextColumn("Next Steps", width="large")
            }
        )
        
        # Delete interface
        interviews_df = delete_rows_interface(interviews_df, save_interviews, "Interviews")
        
        # Download button
        st.download_button(
            label="📥 Download Interviews CSV",
            data=interviews_df.to_csv(index=False),
            file_name=f"interviews_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

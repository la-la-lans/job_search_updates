import streamlit as st
import pandas as pd
import os
from datetime import datetime

DATA_FILE = "job_applications.csv"
COMPANIES_FILE = "companies.csv"
NETWORKING_FILE = "networking.csv"

def load_applications():
    """Load applications from CSV file"""
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # Create empty DataFrame with required columns
        return pd.DataFrame(columns=['date', 'company', 'role', 'status', 'priority', 'salary', 'notes'])

def save_applications(df):
    """Save applications to CSV file"""
    df.to_csv(DATA_FILE, index=False)

def load_companies():
    if os.path.exists(COMPANIES_FILE):
        return pd.read_csv(COMPANIES_FILE)
    else:
        return pd.DataFrame(columns=['company', 'industry', 'size', 'tech_stack', 'rating', 'notes'])

def save_companies(df):
    df.to_csv(COMPANIES_FILE, index=False)

st.set_page_config(page_title="Job Search CRM", layout="wide")

st.title("🎯 Job Search CRM")
page = st.sidebar.selectbox("Navigate", ["📊 Dashboard", "📋 Applications", "🏢 Companies", "🤝 Networking"])

if page == "📊 Dashboard":
    st.header("Dashboard")
    
    # Load data
    applications_df = load_applications()
    
    if not applications_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Applications", len(applications_df))
        
        with col2:
            interviews = len(applications_df[applications_df['status'] == 'Interview'])
            st.metric("Interviews", interviews)
        
        with col3:
            offers = len(applications_df[applications_df['status'] == 'Offer'])
            st.metric("Offers", offers)
        
        with col4:
            if len(applications_df) > 0:
                response_rate = round((interviews + offers) / len(applications_df) * 100, 1)
                st.metric("Response Rate", f"{response_rate}%")
        
        # Charts
        st.subheader("Application Status Distribution")
        status_counts = applications_df['status'].value_counts()
        st.bar_chart(status_counts)
        
        # Recent applications
        st.subheader("Recent Applications")
        recent_apps = applications_df.sort_values('date', ascending=False).head(5)
        st.dataframe(recent_apps)
    else:
        st.info("No applications yet. Add some in the Applications tab!")

elif page == "📋 Applications":
    st.header("Job Applications")
    
    applications_df = load_applications()

    with st.expander("➕ Add New Application", expanded=True):
        with st.form("new_application"):
            col1, col2 = st.columns(2)
            
            with col1:
                company = st.text_input("Company *", placeholder="e.g., Cathay Financial")
                role = st.text_input("Role Title *", placeholder="e.g., Data Analyst")
                date = st.date_input("Date Applied", value=datetime.now())
            
            with col2:
                status = st.selectbox("Status", ["Applied", "Interview", "Rejected", "Offer", "Follow-up"])
                priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                salary = st.text_input("Salary Range", placeholder="NT$800K-1.2M")
            
            notes = st.text_area("Notes", placeholder="Requirements, contact info, etc.")
            
            if st.form_submit_button("💾 Save Application", type="primary"):
                if company and role:
                    # Add new row
                    new_row = pd.DataFrame({
                        'date': [date],
                        'company': [company],
                        'role': [role],
                        'status': [status],
                        'priority': [priority],
                        'salary': [salary],
                        'notes': [notes]
                    })
                    
                    applications_df = pd.concat([applications_df, new_row], ignore_index=True)
                    save_applications(applications_df)
                    st.success(f"✅ Added application for {role} at {company}")
                    st.rerun()
                else:
                    st.error("Please fill in Company and Role fields")
    
    if not applications_df.empty:
        st.subheader(f"All Applications ({len(applications_df)})")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.multiselect("Filter by Status", 
                                         applications_df['status'].unique(),
                                         default=applications_df['status'].unique())
        with col2:
            priority_filter = st.multiselect("Filter by Priority", 
                                           applications_df['priority'].unique(),
                                           default=applications_df['priority'].unique())
        
        filtered_df = applications_df[
            (applications_df['status'].isin(status_filter)) &
            (applications_df['priority'].isin(priority_filter))
        ]
        
        st.dataframe(
            filtered_df,
            use_container_width=True,
            column_config={
                "date": st.column_config.DateColumn("Date Applied"),
                "company": st.column_config.TextColumn("Company"),
                "role": st.column_config.TextColumn("Role"),
                "status": st.column_config.TextColumn("Status"),
                "priority": st.column_config.TextColumn("Priority"),
                "salary": st.column_config.TextColumn("Salary Range"),
                "notes": st.column_config.TextColumn("Notes", width="large")
            }
        )
        
        st.download_button(
            label="📥 Download Applications as CSV",
            data=applications_df.to_csv(index=False),
            file_name=f"job_applications_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
        if st.checkbox("🗑️ Enable Delete Mode"):
            st.warning("⚠️ Delete mode enabled")
            selected_indices = st.multiselect(
                "Select applications to delete:",
                range(len(applications_df)),
                format_func=lambda x: f"{applications_df.iloc[x]['company']} - {applications_df.iloc[x]['role']}"
            )
            
            if selected_indices and st.button("🗑️ Delete Selected", type="secondary"):
                applications_df = applications_df.drop(selected_indices).reset_index(drop=True)
                save_applications(applications_df)
                st.success(f"Deleted {len(selected_indices)} applications")
                st.rerun()

elif page == "🏢 Companies":
    st.header("Company Research")
    
    companies_df = load_companies()
    
    with st.expander("➕ Add Company Research"):
        with st.form("new_company"):
            col1, col2 = st.columns(2)
            
            with col1:
                company = st.text_input("Company Name")
                industry = st.text_input("Industry")
                size = st.selectbox("Company Size", ["<50", "50-200", "200-1000", "1000-5000", "5000+"])
            
            with col2:
                tech_stack = st.text_input("Tech Stack", placeholder="SQL, Python, Tableau")
                rating = st.selectbox("Rating", ["1/5", "2/5", "3/5", "4/5", "5/5"])
            
            notes = st.text_area("Notes", placeholder="Culture, contacts, etc.")
            
            if st.form_submit_button("Save Company"):
                if company:
                    new_company = pd.DataFrame({
                        'company': [company],
                        'industry': [industry], 
                        'size': [size],
                        'tech_stack': [tech_stack],
                        'rating': [rating],
                        'notes': [notes]
                    })
                    
                    companies_df = pd.concat([companies_df, new_company], ignore_index=True)
                    save_companies(companies_df)
                    st.success(f"Added {company} to research")
                    st.rerun()
    
    if not companies_df.empty:
        st.dataframe(companies_df, use_container_width=True)

streamlit run job_search_crm.py

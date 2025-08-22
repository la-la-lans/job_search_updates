# Job Search CRM - Enhanced Streamlit Version with Excel Upload
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io

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

def process_uploaded_excel(uploaded_file):
    """Process uploaded Excel file and return data for each sheet"""
    try:
        # Read all sheets from the Excel file
        xl_file = pd.ExcelFile(uploaded_file)
        sheet_names = xl_file.sheet_names
        
        data_dict = {}
        
        # Define expected sheet names and their corresponding data types
        sheet_mapping = {
            'Applications': 'applications',
            'Companies': 'companies', 
            'Networking': 'networking',
            'Interviews': 'interviews'
        }
        
        for sheet_name in sheet_names:
            try:
                df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                
                # Clean up the data
                df = df.dropna(how='all')  # Remove completely empty rows
                df = df.fillna('')  # Fill NaN values with empty strings
                
                # Map sheet names to data types
                data_type = None
                for expected_sheet, dt in sheet_mapping.items():
                    if expected_sheet.lower() in sheet_name.lower():
                        data_type = dt
                        break
                
                if data_type:
                    data_dict[data_type] = df
                else:
                    # If sheet name doesn't match expected patterns, try to infer from columns
                    columns = [col.lower() for col in df.columns]
                    if 'role_title' in columns or 'job_link' in columns:
                        data_dict['applications'] = df
                    elif 'industry' in columns or 'glassdoor_rating' in columns:
                        data_dict['companies'] = df
                    elif 'contact_name' in columns or 'connection_type' in columns:
                        data_dict['networking'] = df
                    elif 'interview_type' in columns or 'interviewer' in columns:
                        data_dict['interviews'] = df
                        
            except Exception as e:
                st.warning(f"Could not process sheet '{sheet_name}': {str(e)}")
                continue
        
        return data_dict, sheet_names
        
    except Exception as e:
        st.error(f"Error processing Excel file: {str(e)}")
        return {}, []

def validate_and_clean_data(df, data_type):
    """Validate and clean uploaded data based on data type"""
    expected_columns = {
        'applications': ['date_applied', 'company', 'role_title', 'job_link', 'status', 
                        'priority', 'salary_range', 'location', 'next_action', 
                        'follow_up_date', 'notes'],
        'companies': ['company', 'industry', 'size', 'tech_stack', 'culture_notes', 
                     'glassdoor_rating', 'key_contacts', 'open_roles', 'applied_status'],
        'networking': ['contact_name', 'company', 'position', 'connection_type', 
                      'contact_date', 'response', 'meeting_scheduled', 
                      'follow_up_action', 'notes'],
        'interviews': ['company', 'interview_date', 'interview_type', 'interviewer', 
                      'prep_status', 'key_topics', 'questions_to_ask', 'outcome', 'next_steps']
    }
    
    if data_type not in expected_columns:
        return df
    
    # Ensure all expected columns exist
    for col in expected_columns[data_type]:
        if col not in df.columns:
            df[col] = ''
    
    # Reorder columns to match expected structure
    df = df[expected_columns[data_type]]
    
    # Clean date columns
    date_columns = {
        'applications': ['date_applied', 'follow_up_date'],
        'networking': ['contact_date'],
        'companies': [],
        'interviews': []
    }
    
    for date_col in date_columns.get(data_type, []):
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce').dt.strftime('%Y-%m-%d')
            df[date_col] = df[date_col].fillna('')
    
    return df

def create_excel_download():
    """Create Excel file with all current data for download"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Load all current data
        apps_df = load_applications()
        companies_df = load_companies() 
        networking_df = load_networking()
        interviews_df = load_interviews()
        
        # Write each dataframe to a separate sheet
        if not apps_df.empty:
            apps_df.to_excel(writer, sheet_name='Applications', index=False)
        if not companies_df.empty:
            companies_df.to_excel(writer, sheet_name='Companies', index=False)
        if not networking_df.empty:
            networking_df.to_excel(writer, sheet_name='Networking', index=False)
        if not interviews_df.empty:
            interviews_df.to_excel(writer, sheet_name='Interviews', index=False)
    
    return output.getvalue()

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
    ["📊 Dashboard", "📋 Applications", "🏢 Companies", "🤝 Networking", "📝 Interviews", "📤 Data Management"]
)

# Add Excel upload section in sidebar
st.sidebar.markdown("---")
st.sidebar.header("📁 Quick Actions")

# Download current data as Excel
if st.sidebar.button("📥 Download All Data (Excel)", type="secondary"):
    try:
        excel_data = create_excel_download()
        st.sidebar.download_button(
            label="💾 Click to Download Excel File",
            data=excel_data,
            file_name=f"job_search_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.sidebar.error(f"Error creating Excel file: {str(e)}")

# Upload Excel file in sidebar
st.sidebar.subheader("📤 Upload from Backup")
uploaded_file = st.sidebar.file_uploader(
    "Upload Excel File", 
    type=['xlsx', 'xls'],
    help="Upload your Google Sheets export or backup Excel file"
)

if uploaded_file is not None:
    with st.sidebar:
        try:
            data_dict, sheet_names = process_uploaded_excel(uploaded_file)
            
            if data_dict:
                st.success(f"✅ Found {len(data_dict)} data types in {len(sheet_names)} sheets")
                
                # Show what was found
                for data_type, df in data_dict.items():
                    st.write(f"**{data_type.title()}**: {len(df)} records")
                
                # Import options
                st.subheader("Import Options")
                import_mode = st.radio(
                    "How to handle existing data?",
                    ["Replace all", "Append new", "Preview only"],
                    help="Replace: Delete current data and use uploaded data\nAppend: Add uploaded data to existing data\nPreview: Just show what would be imported"
                )
                
                if st.button("🔄 Import Data", type="primary"):
                    if import_mode == "Preview only":
                        st.info("Preview mode - no data was actually imported")
                        for data_type, df in data_dict.items():
                            st.subheader(f"{data_type.title()} Preview")
                            st.dataframe(df.head(), use_container_width=True)
                    else:
                        # Import the data
                        imported_count = 0
                        
                        for data_type, uploaded_df in data_dict.items():
                            try:
                                # Clean and validate the data
                                cleaned_df = validate_and_clean_data(uploaded_df, data_type)
                                
                                if import_mode == "Replace all":
                                    # Replace existing data
                                    if data_type == 'applications':
                                        save_applications(cleaned_df)
                                    elif data_type == 'companies':
                                        save_companies(cleaned_df)
                                    elif data_type == 'networking':
                                        save_networking(cleaned_df)
                                    elif data_type == 'interviews':
                                        save_interviews(cleaned_df)
                                    
                                    imported_count += len(cleaned_df)
                                    st.success(f"✅ Replaced {data_type} with {len(cleaned_df)} records")
                                    
                                elif import_mode == "Append new":
                                    # Append to existing data
                                    if data_type == 'applications':
                                        existing_df = load_applications()
                                        combined_df = pd.concat([existing_df, cleaned_df], ignore_index=True)
                                        save_applications(combined_df)
                                    elif data_type == 'companies':
                                        existing_df = load_companies()
                                        combined_df = pd.concat([existing_df, cleaned_df], ignore_index=True)
                                        save_companies(combined_df)
                                    elif data_type == 'networking':
                                        existing_df = load_networking()
                                        combined_df = pd.concat([existing_df, cleaned_df], ignore_index=True)
                                        save_networking(combined_df)
                                    elif data_type == 'interviews':
                                        existing_df = load_interviews()
                                        combined_df = pd.concat([existing_df, cleaned_df], ignore_index=True)
                                        save_interviews(combined_df)
                                    
                                    imported_count += len(cleaned_df)
                                    st.success(f"✅ Added {len(cleaned_df)} new {data_type} records")
                                    
                            except Exception as e:
                                st.error(f"Error importing {data_type}: {str(e)}")
                        
                        if imported_count > 0:
                            st.balloons()
                            st.success(f"🎉 Successfully imported {imported_count} total records!")
                            st.info("📝 Please refresh the page or navigate to different sections to see the imported data")
            
            else:
                st.error("❌ Could not find valid data in the uploaded file")
                st.info("Make sure your Excel file has sheets named 'Applications', 'Companies', 'Networking', or 'Interviews'")
                
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

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

# Data Management Page
elif page == "📤 Data Management":
    st.header("

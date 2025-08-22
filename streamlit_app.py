# Job Search CRM 
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

# Separate upload sections for each data type
st.sidebar.markdown("---")
st.sidebar.subheader("📤 Upload Individual Files")

# Applications upload
applications_file = st.sidebar.file_uploader(
    "📋 Applications", 
    type=['xlsx', 'xls', 'csv'],
    key="applications_upload",
    help="Upload Applications data"
)

# Companies upload
companies_file = st.sidebar.file_uploader(
    "🏢 Companies", 
    type=['xlsx', 'xls', 'csv'],
    key="companies_upload",
    help="Upload Companies data"
)

# Networking upload
networking_file = st.sidebar.file_uploader(
    "🤝 Networking", 
    type=['xlsx', 'xls', 'csv'],
    key="networking_upload",
    help="Upload Networking data"
)

# Interviews upload
interviews_file = st.sidebar.file_uploader(
    "📝 Interviews", 
    type=['xlsx', 'xls', 'csv'],
    key="interviews_upload",
    help="Upload Interviews data"
)

# Process individual uploads
uploaded_files = {
    'applications': applications_file,
    'companies': companies_file,
    'networking': networking_file,
    'interviews': interviews_file
}

for data_type, uploaded_file in uploaded_files.items():
    if uploaded_file is not None:
        with st.sidebar:
            try:
                # Read the file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Clean up the data
                df = df.dropna(how='all')  # Remove completely empty rows
                df = df.fillna('')  # Fill NaN values with empty strings
                
                st.success(f"✅ Loaded {data_type}: {len(df)} records")
                
                # Import options
                import_mode = st.radio(
                    f"Import {data_type.title()}:",
                    ["Replace all", "Append new", "Preview"],
                    key=f"{data_type}_import_mode",
                    help="Replace: Delete current data\nAppend: Add to existing\nPreview: Just show data"
                )
                
                if st.button(f"Import {data_type.title()}", key=f"import_{data_type}", type="primary"):
                    if import_mode == "Preview":
                        st.info("Preview mode - showing first 5 rows:")
                        st.dataframe(df.head(), use_container_width=True)
                    else:
                        try:
                            # Clean and validate the data
                            cleaned_df = validate_and_clean_data(df, data_type)
                            
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
                                
                                st.success(f"✅ Added {len(cleaned_df)} new {data_type} records")
                            
                            st.info("Navigate to other sections to see imported data")
                            
                        except Exception as e:
                            st.error(f"Error importing {data_type}: {str(e)}")
                            
            except Exception as e:
                st.error(f"Error reading {data_type} file: {str(e)}")

# Bulk upload option
st.sidebar.markdown("---")
st.sidebar.subheader("📤 Bulk Upload (Multi-sheet)")
bulk_file = st.sidebar.file_uploader(
    "Upload Multi-sheet Excel", 
    type=['xlsx', 'xls'],
    key="bulk_upload",
    help="Upload Excel file with multiple sheets"
)

if bulk_file is not None:
    with st.sidebar:
        try:
            data_dict, sheet_names = process_uploaded_excel(bulk_file)
            
            if data_dict:
                st.success(f"✅ Found {len(data_dict)} data types in {len(sheet_names)} sheets")
                
                # Show what was found
                for data_type, df in data_dict.items():
                    st.write(f"**{data_type.title()}**: {len(df)} records")
                
                # Import options
                bulk_import_mode = st.radio(
                    "Bulk import mode:",
                    ["Replace all", "Append new", "Preview only"],
                    key="bulk_import_mode",
                    help="Replace: Delete current data\nAppend: Add to existing\nPreview: Just show what would be imported"
                )
                
                if st.button("🔄 Import All", key="bulk_import", type="primary"):
                    if bulk_import_mode == "Preview only":
                        st.info("Preview mode - no data imported")
                        for data_type, df in data_dict.items():
                            with st.expander(f"{data_type.title()} Preview"):
                                st.dataframe(df.head(), use_container_width=True)
                    else:
                        # Import the data
                        imported_count = 0
                        
                        for data_type, uploaded_df in data_dict.items():
                            try:
                                # Clean and validate the data
                                cleaned_df = validate_and_clean_data(uploaded_df, data_type)
                                
                                if bulk_import_mode == "Replace all":
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
                                    st.success(f"✅ Replaced {data_type}: {len(cleaned_df)} records")
                                    
                                elif bulk_import_mode == "Append new":
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
                                    st.success(f"✅ Added {len(cleaned_df)} {data_type} records")
                                    
                            except Exception as e:
                                st.error(f"Error importing {data_type}: {str(e)}")
                        
                        if imported_count > 0:
                            st.balloons()
                            st.success(f"🎉 Imported {imported_count} total records!")
            
            else:
                st.error("❌ No valid data found in file")
                
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
    st.header("📤 Data Management")
    
    st.markdown("Manage your job search data - backup, restore, and export options")
    
    # Current data overview
    st.subheader("📊 Current Data Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    applications_df = load_applications()
    companies_df = load_companies()
    networking_df = load_networking()
    interviews_df = load_interviews()
    
    with col1:
        st.metric("Applications", len(applications_df))
    with col2:
        st.metric("Companies", len(companies_df))
    with col3:
        st.metric("Networking", len(networking_df))
    with col4:
        st.metric("Interviews", len(interviews_df))
    
    # Export section
    st.subheader("📥 Export Data")
    st.markdown("Download your data for backup or to use with Google Sheets")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Excel download
        if st.button("📊 Download Excel File", type="primary"):
            try:
                excel_data = create_excel_download()
                st.download_button(
                    label="💾 Click to Download Excel",
                    data=excel_data,
                    file_name=f"job_search_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.success("✅ Excel file ready for download!")
            except Exception as e:
                st.error(f"Error creating Excel file: {str(e)}")
    
    with col2:
        # Individual CSV downloads
        st.markdown("**Individual CSV Files:**")
        
        if not applications_df.empty:
            st.download_button(
                "📋 Applications CSV",
                applications_df.to_csv(index=False),
                f"applications_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
        
        if not companies_df.empty:
            st.download_button(
                "🏢 Companies CSV",
                companies_df.to_csv(index=False),
                f"companies_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
        
        if not networking_df.empty:
            st.download_button(
                "🤝 Networking CSV",
                networking_df.to_csv(index=False),
                f"networking_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
        
        if not interviews_df.empty:
            st.download_button(
                "📝 Interviews CSV",
                interviews_df.to_csv(index=False),
                f"interviews_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv"
            )
    
    st.markdown("---")
    
    # Import section
    st.subheader("📤 Import Data")
    st.markdown("Upload Excel files from Google Sheets or other backups")
    
    uploaded_file = st.file_uploader(
        "Choose Excel file", 
        type=['xlsx', 'xls'],
        help="Upload Excel file with your job search data. Sheets should be named: Applications, Companies, Networking, Interviews"
    )
    
    if uploaded_file is not None:
        try:
            data_dict, sheet_names = process_uploaded_excel(uploaded_file)
            
            if data_dict:
                st.success(f"✅ Successfully processed Excel file!")
                st.info(f"Found {len(sheet_names)} sheets: {', '.join(sheet_names)}")
                
                # Show preview of data
                st.subheader("📋 Data Preview")
                
                for data_type, df in data_dict.items():
                    with st.expander(f"Preview {data_type.title()} ({len(df)} records)"):
                        st.dataframe(df.head(10), use_container_width=True)
                
                # Import options
                st.subheader("⚙️ Import Settings")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    import_mode = st.radio(
                        "Import Mode",
                        ["Replace all data", "Append to existing data", "Preview only"],
                        help="Replace: Delete current data and use uploaded data\nAppend: Add uploaded data to existing data\nPreview: Just show what would be imported"
                    )
                
                with col2:
                    selected_types = st.multiselect(
                        "Select data types to import",
                        list(data_dict.keys()),
                        default=list(data_dict.keys())
                    )
                
                if st.button("🚀 Import Selected Data", type="primary"):
                    if import_mode == "Preview only":
                        st.info("Preview mode - no data was actually imported")
                    else:
                        imported_count = 0
                        errors = []
                        
                        for data_type in selected_types:
                            if data_type not in data_dict:
                                continue
                                
                            try:
                                uploaded_df = data_dict[data_type]
                                cleaned_df = validate_and_clean_data(uploaded_df, data_type)
                                
                                if import_mode == "Replace all data":
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
                                    
                                elif import_mode == "Append to existing data":
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
                                error_msg = f"Error importing {data_type}: {str(e)}"
                                errors.append(error_msg)
                                st.error(error_msg)
                        
                        if imported_count > 0:
                            st.balloons()
                            st.success(f"🎉 Successfully imported {imported_count} total records!")
                            
                            if errors:
                                st.warning("⚠️ Some errors occurred during import - check the messages above")
                            
                            st.info("📝 Navigate to other sections to see your imported data")
                        
                        elif errors:
                            st.error("❌ Import failed - check the error messages above")
            
            else:
                st.error("❌ Could not find valid data in the uploaded file")
                st.info("💡 Make sure your Excel file has sheets named 'Applications', 'Companies', 'Networking', or 'Interviews' with the correct column structure")
                
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
    
    # Instructions
    st.markdown("---")
    st.subheader("📖 Instructions")
    
    with st.expander("How to use with Google Sheets"):
        st.markdown("""
        **To backup your data to Google Sheets:**
        1. Click "Download Excel File" above
        2. Open Google Sheets
        3. Create a new spreadsheet
        4. Go to File → Import → Upload
        5. Select your downloaded Excel file
        6. Choose "Replace spreadsheet" 
        
        **To restore from Google Sheets:**
        1. Open your Google Sheets backup
        2. Go to File → Download → Microsoft Excel (.xlsx)
        3. Upload the downloaded file using the "Import Data" section above
        4. Choose your import mode and click "Import Selected Data"
        
        **Sheet Names:** Make sure your Google Sheets has tabs named:
        - Applications
        - Companies  
        - Networking
        - Interviews
        """)
    
    with st.expander("Column Requirements"):
        st.markdown("""
        **Applications sheet should have columns:**
        `date_applied, company, role_title, job_link, status, priority, salary_range, location, next_action, follow_up_date, notes`
        
        **Companies sheet should have columns:**
        `company, industry, size, tech_stack, culture_notes, glassdoor_rating, key_contacts, open_roles, applied_status`
        
        **Networking sheet should have columns:**
        `contact_name, company, position, connection_type, contact_date, response, meeting_scheduled, follow_up_action, notes`
        
        **Interviews sheet should have columns:**
        `company, interview_date, interview_type, interviewer, prep_status, key_topics, questions_to_ask, outcome, next_steps`
        """)

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

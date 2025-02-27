import streamlit as st
import pandas as pd
import os
import json
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import openai
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EmailAlerts")

class EmailAlertManager:
    """Manages email alerts and notifications for investor updates"""
    
    def __init__(self):
        """Initialize the email alert manager"""
        self.logger = logging.getLogger("EmailAlerts")
        
        # Initialize OpenAI client if API key is available
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
            self.api_available = True
        else:
            self.api_available = False
            self.logger.warning("OpenAI API key not set. Using simplified email templates.")
        
        # Load saved alerts if available
        self.alerts_file = "email_alerts.json"
        self.alerts = self._load_alerts()
        
        self.logger.info("EmailAlertManager initialized")
    
    def _load_alerts(self) -> Dict[str, Any]:
        """Load saved alerts from file"""
        try:
            if os.path.exists(self.alerts_file):
                with open(self.alerts_file, 'r') as f:
                    return json.load(f)
            return {"users": {}, "alerts": []}
        except Exception as e:
            self.logger.error(f"Error loading alerts: {str(e)}")
            return {"users": {}, "alerts": []}
    
    def _save_alerts(self) -> bool:
        """Save alerts to file"""
        try:
            with open(self.alerts_file, 'w') as f:
                json.dump(self.alerts, f, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving alerts: {str(e)}")
            return False
    
    def create_alert(self, 
                    email: str, 
                    name: str, 
                    search_criteria: Dict[str, Any], 
                    frequency: str = "daily",
                    alert_type: str = "new_investors") -> bool:
        """
        Create a new email alert
        
        Args:
            email: User's email address
            name: User's name
            search_criteria: Search criteria for matching investors
            frequency: Alert frequency (daily, weekly, monthly)
            alert_type: Type of alert (new_investors, updates, market_changes)
            
        Returns:
            Success status
        """
        try:
            # Create user if not exists
            if email not in self.alerts["users"]:
                self.alerts["users"][email] = {
                    "name": name,
                    "email": email,
                    "created_at": datetime.now().isoformat(),
                    "preferences": {
                        "frequency": frequency,
                        "alert_types": [alert_type]
                    }
                }
            
            # Create alert
            alert_id = f"alert_{len(self.alerts['alerts']) + 1}"
            alert = {
                "id": alert_id,
                "user_email": email,
                "name": f"{name}'s {alert_type.replace('_', ' ')} alert",
                "search_criteria": search_criteria,
                "frequency": frequency,
                "alert_type": alert_type,
                "created_at": datetime.now().isoformat(),
                "last_sent": None,
                "active": True
            }
            
            self.alerts["alerts"].append(alert)
            self._save_alerts()
            
            self.logger.info(f"Created alert {alert_id} for {email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating alert: {str(e)}")
            return False
    
    def update_alert(self, alert_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing alert"""
        try:
            for i, alert in enumerate(self.alerts["alerts"]):
                if alert["id"] == alert_id:
                    for key, value in updates.items():
                        if key in alert and key not in ["id", "user_email", "created_at"]:
                            alert[key] = value
                    
                    self.alerts["alerts"][i] = alert
                    self._save_alerts()
                    
                    self.logger.info(f"Updated alert {alert_id}")
                    return True
            
            self.logger.warning(f"Alert {alert_id} not found")
            return False
            
        except Exception as e:
            self.logger.error(f"Error updating alert: {str(e)}")
            return False
    
    def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert"""
        try:
            for i, alert in enumerate(self.alerts["alerts"]):
                if alert["id"] == alert_id:
                    del self.alerts["alerts"][i]
                    self._save_alerts()
                    
                    self.logger.info(f"Deleted alert {alert_id}")
                    return True
            
            self.logger.warning(f"Alert {alert_id} not found")
            return False
            
        except Exception as e:
            self.logger.error(f"Error deleting alert: {str(e)}")
            return False
    
    def get_user_alerts(self, email: str) -> List[Dict[str, Any]]:
        """Get all alerts for a user"""
        try:
            return [alert for alert in self.alerts["alerts"] if alert["user_email"] == email]
        except Exception as e:
            self.logger.error(f"Error getting user alerts: {str(e)}")
            return []
    
    def update_user_preferences(self, email: str, preferences: Dict[str, Any]) -> bool:
        """Update user notification preferences"""
        try:
            if email in self.alerts["users"]:
                for key, value in preferences.items():
                    if key in self.alerts["users"][email]["preferences"]:
                        self.alerts["users"][email]["preferences"][key] = value
                
                self._save_alerts()
                self.logger.info(f"Updated preferences for {email}")
                return True
            
            self.logger.warning(f"User {email} not found")
            return False
            
        except Exception as e:
            self.logger.error(f"Error updating user preferences: {str(e)}")
            return False
    
    def send_test_email(self, email: str, alert_id: Optional[str] = None) -> bool:
        """Send a test email notification"""
        try:
            # Get user info
            if email not in self.alerts["users"]:
                self.logger.warning(f"User {email} not found")
                return False
            
            user = self.alerts["users"][email]
            
            # Get alert info if specified
            alert = None
            if alert_id:
                for a in self.alerts["alerts"]:
                    if a["id"] == alert_id and a["user_email"] == email:
                        alert = a
                        break
                
                if not alert:
                    self.logger.warning(f"Alert {alert_id} not found for {email}")
                    return False
            
            # Create email content
            subject = "Test Alert from Investor Search Platform"
            
            if alert:
                body = f"""
                <html>
                <body>
                <h2>Test Alert: {alert['name']}</h2>
                <p>Hello {user['name']},</p>
                <p>This is a test email for your alert: <strong>{alert['name']}</strong></p>
                <p>Alert type: {alert['alert_type'].replace('_', ' ').title()}</p>
                <p>Frequency: {alert['frequency'].title()}</p>
                <p>This alert will notify you about investors matching your criteria:</p>
                <ul>
                """
                
                for key, value in alert['search_criteria'].items():
                    if value and isinstance(value, (list, tuple)) and len(value) > 0:
                        body += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {', '.join(str(v) for v in value)}</li>"
                    elif value:
                        body += f"<li><strong>{key.replace('_', ' ').title()}:</strong> {value}</li>"
                
                body += """
                </ul>
                <p>Thank you for using our Investor Search Platform!</p>
                </body>
                </html>
                """
            else:
                body = f"""
                <html>
                <body>
                <h2>Test Email Notification</h2>
                <p>Hello {user['name']},</p>
                <p>This is a test email from the Investor Search Platform.</p>
                <p>Your notification preferences:</p>
                <ul>
                <li><strong>Frequency:</strong> {user['preferences']['frequency'].title()}</li>
                <li><strong>Alert Types:</strong> {', '.join(t.replace('_', ' ').title() for t in user['preferences']['alert_types'])}</li>
                </ul>
                <p>Thank you for using our Investor Search Platform!</p>
                </body>
                </html>
                """
            
            # In a real application, you would send the email here
            # For this demo, we'll just log it
            self.logger.info(f"Test email would be sent to {email} with subject: {subject}")
            
            # Display success in Streamlit
            st.success(f"Test email would be sent to {email}")
            st.info("Note: In a production environment, this would send an actual email.")
            
            # Show email preview
            with st.expander("Email Preview"):
                st.markdown(body, unsafe_allow_html=True)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending test email: {str(e)}")
            st.error(f"Error sending test email: {str(e)}")
            return False
    
    def generate_email_content(self, alert: Dict[str, Any], investors_df: pd.DataFrame) -> str:
        """Generate personalized email content based on alert and matching investors"""
        try:
            if self.api_available and len(investors_df) > 0:
                # Use OpenAI to generate personalized content
                user = self.alerts["users"][alert["user_email"]]
                
                # Create a summary of the investors
                investor_summaries = []
                for _, investor in investors_df.head(5).iterrows():
                    summary = f"{investor['name']} ({investor['type']}): {investor['location']}, " \
                             f"Investments: {investor['investments']}, " \
                             f"Stages: {', '.join(investor['investment_stages'])}"
                    investor_summaries.append(summary)
                
                investors_text = "\n".join(investor_summaries)
                
                # Generate personalized content with OpenAI
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an expert assistant for a venture capital and investor search platform. Write personalized, professional email content."},
                        {"role": "user", "content": f"""
                        Create a professional email for an investor alert notification with the following details:
                        
                        User: {user['name']}
                        Alert Type: {alert['alert_type'].replace('_', ' ').title()}
                        Alert Name: {alert['name']}
                        
                        Matching Investors:
                        {investors_text}
                        
                        Include a personalized greeting, a summary of why these investors match their criteria, 
                        and a call to action to view more details on the platform. Format as HTML.
                        """}
                    ],
                    max_tokens=800
                )
                
                content = response.choices[0].message.content
                return content
            else:
                # Use template-based approach
                user = self.alerts["users"][alert["user_email"]]
                
                content = f"""
                <html>
                <body>
                <h2>{alert['name']}</h2>
                <p>Hello {user['name']},</p>
                <p>We've found {len(investors_df)} investors matching your criteria:</p>
                <ul>
                """
                
                for _, investor in investors_df.head(5).iterrows():
                    content += f"""
                    <li>
                        <strong>{investor['name']}</strong> ({investor['type']})
                        <br>Location: {investor['location']}
                        <br>Investments: {investor['investments']}
                        <br>Stages: {', '.join(investor['investment_stages'])}
                    </li>
                    <br>
                    """
                
                content += """
                </ul>
                <p><a href="#">View all matching investors on the platform</a></p>
                <p>Thank you for using our Investor Search Platform!</p>
                </body>
                </html>
                """
                
                return content
                
        except Exception as e:
            self.logger.error(f"Error generating email content: {str(e)}")
            # Fallback to simple template
            return f"""
            <html>
            <body>
            <h2>Investor Alert</h2>
            <p>We've found {len(investors_df)} investors matching your criteria.</p>
            <p><a href="#">View them on the platform</a></p>
            </body>
            </html>
            """

class EmailAlertSystem:
    """System for managing email alerts for investor updates"""
    
    def __init__(self):
        """Initialize the email alert system"""
        # In a real application, this would connect to an email service
        # For this demo, we'll just store alerts in session state
        if 'email_alerts' not in st.session_state:
            st.session_state.email_alerts = []
        
        # Load saved alerts if available
        self.load_alerts()
    
    def create_alert(self, 
                    email: str, 
                    alert_name: str,
                    investors: List[str],
                    frequency: str,
                    alert_type: str,
                    keywords: Optional[List[str]] = None) -> bool:
        """
        Create a new email alert
        
        Args:
            email: User's email address
            alert_name: Name of the alert
            investors: List of investor names to track
            frequency: Alert frequency (daily, weekly, monthly)
            alert_type: Type of alert (news, funding, all)
            keywords: Optional list of keywords to track
            
        Returns:
            Boolean indicating success
        """
        # Validate email
        if not self._validate_email(email):
            return False
        
        # Create alert object
        alert = {
            "id": len(st.session_state.email_alerts) + 1,
            "email": email,
            "name": alert_name,
            "investors": investors,
            "frequency": frequency,
            "type": alert_type,
            "keywords": keywords if keywords else [],
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_sent": None,
            "status": "active"
        }
        
        # Add to alerts list
        st.session_state.email_alerts.append(alert)
        
        # Save alerts
        self.save_alerts()
        
        return True
    
    def update_alert(self, alert_id: int, updates: Dict[str, Any]) -> bool:
        """
        Update an existing alert
        
        Args:
            alert_id: ID of the alert to update
            updates: Dictionary of fields to update
            
        Returns:
            Boolean indicating success
        """
        # Find alert by ID
        for i, alert in enumerate(st.session_state.email_alerts):
            if alert["id"] == alert_id:
                # Update fields
                for key, value in updates.items():
                    if key in alert:
                        alert[key] = value
                
                # Update in session state
                st.session_state.email_alerts[i] = alert
                
                # Save alerts
                self.save_alerts()
                
                return True
        
        return False
    
    def delete_alert(self, alert_id: int) -> bool:
        """
        Delete an alert
        
        Args:
            alert_id: ID of the alert to delete
            
        Returns:
            Boolean indicating success
        """
        # Find alert by ID
        for i, alert in enumerate(st.session_state.email_alerts):
            if alert["id"] == alert_id:
                # Remove from list
                st.session_state.email_alerts.pop(i)
                
                # Save alerts
                self.save_alerts()
                
                return True
        
        return False
    
    def get_alerts(self, email: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all alerts or alerts for a specific email
        
        Args:
            email: Optional email to filter by
            
        Returns:
            List of alert dictionaries
        """
        if email:
            return [alert for alert in st.session_state.email_alerts if alert["email"] == email]
        else:
            return st.session_state.email_alerts
    
    def save_alerts(self):
        """Save alerts to session state"""
        # In a real application, this would save to a database
        # For this demo, we'll just keep it in session state
        pass
    
    def load_alerts(self):
        """Load saved alerts"""
        # In a real application, this would load from a database
        # For this demo, we'll just use what's in session state
        pass
    
    def _validate_email(self, email: str) -> bool:
        """
        Validate email format
        
        Args:
            email: Email address to validate
            
        Returns:
            Boolean indicating if email is valid
        """
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))
    
    def send_test_alert(self, email: str, alert_name: str) -> bool:
        """
        Send a test alert email
        
        Args:
            email: Email address to send to
            alert_name: Name of the alert
            
        Returns:
            Boolean indicating success
        """
        # In a real application, this would send an actual email
        # For this demo, we'll just return success
        if not self._validate_email(email):
            return False
        
        # Simulate sending email
        st.success(f"Test alert '{alert_name}' would be sent to {email}")
        return True

def render_email_alerts_section(df: Optional[pd.DataFrame] = None):
    """
    Render the email alerts section in the Streamlit app
    
    Args:
        df: Optional DataFrame containing investor data
    """
    st.header("Email Alerts")
    
    # Add description
    st.markdown("""
    Set up email alerts to stay updated on investor activities and news.
    Get notified when there are new funding rounds, news mentions, or other updates
    about the investors you're tracking.
    """)
    
    # Initialize alert system
    alert_system = EmailAlertSystem()
    
    # Create tabs for different sections
    tab1, tab2 = st.tabs(["Create Alert", "Manage Alerts"])
    
    with tab1:
        st.subheader("Create New Alert")
        
        # Create form for alert creation
        with st.form("create_alert_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                email = st.text_input(
                    "Email Address",
                    placeholder="your.email@example.com"
                )
                
                alert_name = st.text_input(
                    "Alert Name",
                    placeholder="e.g., Top VC Updates"
                )
                
                frequency = st.selectbox(
                    "Alert Frequency",
                    options=["Daily", "Weekly", "Monthly"]
                )
            
            with col2:
                alert_type = st.selectbox(
                    "Alert Type",
                    options=["All Updates", "Funding News", "Press Mentions"]
                )
                
                keywords = st.text_input(
                    "Keywords (optional)",
                    placeholder="Enter keywords separated by commas"
                )
            
            # Investor selection
            if df is not None and not df.empty:
                investor_options = df['name'].tolist()
                selected_investors = st.multiselect(
                    "Select Investors to Track",
                    options=investor_options,
                    default=investor_options[:3] if len(investor_options) >= 3 else investor_options
                )
            else:
                selected_investors = []
                st.warning("No investors available. Please search for investors first.")
            
            # Submit button
            submitted = st.form_submit_button("Create Alert")
        
        # Process form submission
        if submitted:
            if not email or not alert_name:
                st.error("Email address and alert name are required")
            elif not selected_investors:
                st.error("Please select at least one investor to track")
            else:
                # Parse keywords
                keyword_list = [k.strip() for k in keywords.split(",") if k.strip()] if keywords else []
                
                # Create alert
                success = alert_system.create_alert(
                    email=email,
                    alert_name=alert_name,
                    investors=selected_investors,
                    frequency=frequency,
                    alert_type=alert_type,
                    keywords=keyword_list
                )
                
                if success:
                    st.success(f"Alert '{alert_name}' created successfully!")
                    
                    # Offer to send test alert
                    if st.button("Send Test Alert"):
                        alert_system.send_test_alert(email, alert_name)
                else:
                    st.error("Failed to create alert. Please check your email address.")
    
    with tab2:
        st.subheader("Manage Your Alerts")
        
        # Email input for filtering alerts
        filter_email = st.text_input(
            "Enter your email to view your alerts",
            placeholder="your.email@example.com"
        )
        
        if filter_email:
            # Get alerts for this email
            alerts = alert_system.get_alerts(filter_email)
            
            if alerts:
                st.write(f"Found {len(alerts)} alerts for {filter_email}")
                
                # Display alerts
                for alert in alerts:
                    with st.expander(f"{alert['name']} ({alert['frequency']})"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Alert ID:** {alert['id']}")
                            st.write(f"**Type:** {alert['type']}")
                            st.write(f"**Created:** {alert['created_at']}")
                            st.write(f"**Status:** {alert['status']}")
                            
                            st.write("**Tracking Investors:**")
                            for investor in alert['investors']:
                                st.markdown(f"- {investor}")
                            
                            if alert['keywords']:
                                st.write("**Keywords:**")
                                for keyword in alert['keywords']:
                                    st.markdown(f"- {keyword}")
                        
                        with col2:
                            # Edit button
                            if st.button("Edit", key=f"edit_{alert['id']}"):
                                st.session_state.editing_alert = alert
                            
                            # Delete button
                            if st.button("Delete", key=f"delete_{alert['id']}"):
                                if alert_system.delete_alert(alert['id']):
                                    st.success(f"Alert '{alert['name']}' deleted successfully")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete alert")
                            
                            # Pause/Resume button
                            status_label = "Pause" if alert['status'] == "active" else "Resume"
                            if st.button(status_label, key=f"status_{alert['id']}"):
                                new_status = "paused" if alert['status'] == "active" else "active"
                                if alert_system.update_alert(alert['id'], {"status": new_status}):
                                    st.success(f"Alert '{alert['name']}' {status_label.lower()}d successfully")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to {status_label.lower()} alert")
                
                # Check if we're editing an alert
                if 'editing_alert' in st.session_state:
                    alert = st.session_state.editing_alert
                    st.write("### Edit Alert")
                    
                    # Create form for editing
                    with st.form("edit_alert_form"):
                        alert_name = st.text_input("Alert Name", value=alert['name'])
                        frequency = st.selectbox("Frequency", options=["Daily", "Weekly", "Monthly"], index=["Daily", "Weekly", "Monthly"].index(alert['frequency']))
                        alert_type = st.selectbox("Type", options=["All Updates", "Funding News", "Press Mentions"], index=["All Updates", "Funding News", "Press Mentions"].index(alert['type']))
                        
                        # Keywords
                        keywords = st.text_input("Keywords (comma-separated)", value=", ".join(alert['keywords']))
                        
                        # Investor selection
                        if df is not None and not df.empty:
                            investor_options = df['name'].tolist()
                            selected_investors = st.multiselect(
                                "Investors to Track",
                                options=investor_options,
                                default=alert['investors']
                            )
                        else:
                            selected_investors = alert['investors']
                            st.write(f"**Currently tracking:** {', '.join(selected_investors)}")
                        
                        # Submit button
                        update_submitted = st.form_submit_button("Update Alert")
                    
                    # Process form submission
                    if update_submitted:
                        if not alert_name:
                            st.error("Alert name is required")
                        elif not selected_investors:
                            st.error("Please select at least one investor to track")
                        else:
                            # Parse keywords
                            keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
                            
                            # Update alert
                            updates = {
                                "name": alert_name,
                                "frequency": frequency,
                                "type": alert_type,
                                "keywords": keyword_list,
                                "investors": selected_investors
                            }
                            
                            success = alert_system.update_alert(alert['id'], updates)
                            
                            if success:
                                st.success(f"Alert '{alert_name}' updated successfully!")
                                # Clear editing state
                                del st.session_state.editing_alert
                                st.rerun()
                            else:
                                st.error("Failed to update alert")
                    
                    # Cancel button
                    if st.button("Cancel Edit"):
                        del st.session_state.editing_alert
                        st.rerun()
            else:
                st.info(f"No alerts found for {filter_email}")
                st.write("Create a new alert in the 'Create Alert' tab.")
        else:
            st.info("Enter your email address to view and manage your alerts")
    
    # Add information about alert functionality
    st.markdown("---")
    st.markdown("""
    ### About Email Alerts
    
    Our email alert system helps you stay updated on investor activities without having to manually check for updates.
    
    **Alert Types:**
    - **All Updates**: Receive all types of updates about the selected investors
    - **Funding News**: Get notified when the investors make new investments
    - **Press Mentions**: Receive alerts when the investors are mentioned in news articles
    
    **Frequency Options:**
    - **Daily**: Receive updates every day (if there are any)
    - **Weekly**: Get a weekly digest of updates
    - **Monthly**: Receive a monthly summary of investor activities
    
    **Keywords:**
    Add specific keywords to filter the updates you receive. For example, if you're interested in AI investments,
    add keywords like "artificial intelligence", "machine learning", or "AI".
    """) 
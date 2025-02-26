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

def render_email_alerts_section(investors_df: pd.DataFrame = None):
    """Render the email alerts and notifications section"""
    st.header("Email Alerts & Notifications")
    
    # Initialize alert manager
    alert_manager = EmailAlertManager()
    
    # Create tabs for different sections
    tabs = st.tabs(["My Alerts", "Create Alert", "Notification Settings"])
    
    with tabs[0]:
        st.subheader("My Email Alerts")
        
        # Email input for retrieving alerts
        email = st.text_input("Enter your email to view your alerts:", key="view_alerts_email")
        
        if email:
            user_alerts = alert_manager.get_user_alerts(email)
            
            if user_alerts:
                st.success(f"Found {len(user_alerts)} alerts for {email}")
                
                for alert in user_alerts:
                    with st.expander(f"{alert['name']} ({alert['frequency'].title()})"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Type:** {alert['alert_type'].replace('_', ' ').title()}")
                            st.write(f"**Created:** {alert['created_at'][:10]}")
                            
                            st.write("**Search Criteria:**")
                            criteria_text = ""
                            for key, value in alert['search_criteria'].items():
                                if value and isinstance(value, (list, tuple)) and len(value) > 0:
                                    criteria_text += f"- {key.replace('_', ' ').title()}: {', '.join(str(v) for v in value)}\n"
                                elif value:
                                    criteria_text += f"- {key.replace('_', ' ').title()}: {value}\n"
                            
                            st.markdown(criteria_text)
                        
                        with col2:
                            # Toggle active status
                            is_active = st.toggle("Active", value=alert['active'], key=f"toggle_{alert['id']}")
                            if is_active != alert['active']:
                                alert_manager.update_alert(alert['id'], {"active": is_active})
                                st.experimental_rerun()
                            
                            # Send test email
                            if st.button("Test Email", key=f"test_{alert['id']}"):
                                alert_manager.send_test_email(email, alert['id'])
                            
                            # Delete alert
                            if st.button("Delete", key=f"delete_{alert['id']}"):
                                if alert_manager.delete_alert(alert['id']):
                                    st.success("Alert deleted successfully")
                                    st.experimental_rerun()
                                else:
                                    st.error("Failed to delete alert")
            else:
                st.info(f"No alerts found for {email}. Create a new alert in the 'Create Alert' tab.")
    
    with tabs[1]:
        st.subheader("Create New Alert")
        
        # User information
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Your Name:", key="create_name")
        with col2:
            email = st.text_input("Your Email:", key="create_email")
        
        # Alert details
        alert_type = st.selectbox(
            "Alert Type:",
            ["new_investors", "investor_updates", "market_changes", "funding_announcements"],
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        frequency = st.select_slider(
            "Alert Frequency:",
            options=["daily", "weekly", "monthly"],
            value="weekly",
            format_func=lambda x: x.title()
        )
        
        # Search criteria
        st.subheader("Search Criteria")
        st.info("Define the criteria for investors you want to be alerted about.")
        
        criteria_col1, criteria_col2 = st.columns(2)
        
        with criteria_col1:
            investor_types = st.multiselect(
                "Investor Types:",
                ["Venture Capital", "Angel Investor", "Private Equity", "Accelerator", "Incubator"],
                default=[]
            )
            
            investment_stages = st.multiselect(
                "Investment Stages:",
                ["Pre-Seed", "Seed", "Series A", "Series B", "Series C", "Growth", "Late Stage"],
                default=[]
            )
            
            min_investments = st.number_input("Minimum Investments:", min_value=0, value=0)
        
        with criteria_col2:
            locations = st.text_input("Locations (comma-separated):")
            
            sectors = st.multiselect(
                "Sectors:",
                ["Technology", "Healthcare", "Finance", "Consumer", "Enterprise", "AI/ML", 
                 "Blockchain", "SaaS", "E-commerce", "Mobile", "IoT", "Clean Tech"],
                default=[]
            )
            
            keywords = st.text_input("Keywords (comma-separated):")
        
        # Create search criteria dictionary
        search_criteria = {
            "investor_types": investor_types,
            "investment_stages": investment_stages,
            "min_investments": min_investments,
            "locations": [loc.strip() for loc in locations.split(",")] if locations else [],
            "sectors": sectors,
            "keywords": [kw.strip() for kw in keywords.split(",")] if keywords else []
        }
        
        # Create alert button
        if st.button("Create Alert", type="primary"):
            if not name or not email:
                st.error("Please enter your name and email")
            elif not any(value for value in search_criteria.values() if value):
                st.error("Please specify at least one search criterion")
            else:
                if alert_manager.create_alert(email, name, search_criteria, frequency, alert_type):
                    st.success("Alert created successfully!")
                    
                    # Send test email
                    if st.button("Send Test Email"):
                        user_alerts = alert_manager.get_user_alerts(email)
                        if user_alerts:
                            alert_manager.send_test_email(email, user_alerts[-1]["id"])
                else:
                    st.error("Failed to create alert")
    
    with tabs[2]:
        st.subheader("Notification Settings")
        
        # Email input for retrieving user
        email = st.text_input("Enter your email:", key="settings_email")
        
        if email:
            # Check if user exists
            if email in alert_manager.alerts["users"]:
                user = alert_manager.alerts["users"][email]
                
                st.success(f"Found settings for {user['name']} ({email})")
                
                # Notification preferences
                st.subheader("Email Preferences")
                
                # Frequency
                current_frequency = user["preferences"].get("frequency", "weekly")
                new_frequency = st.select_slider(
                    "Default Alert Frequency:",
                    options=["daily", "weekly", "monthly"],
                    value=current_frequency,
                    format_func=lambda x: x.title()
                )
                
                # Alert types
                current_types = user["preferences"].get("alert_types", ["new_investors"])
                new_types = st.multiselect(
                    "Alert Types:",
                    ["new_investors", "investor_updates", "market_changes", "funding_announcements"],
                    default=current_types,
                    format_func=lambda x: x.replace('_', ' ').title()
                )
                
                # Digest format
                current_format = user["preferences"].get("digest_format", "individual")
                new_format = st.radio(
                    "Email Format:",
                    ["individual", "digest"],
                    index=0 if current_format == "individual" else 1,
                    format_func=lambda x: "Individual Alerts" if x == "individual" else "Daily Digest"
                )
                
                # Update preferences
                if st.button("Update Preferences"):
                    preferences = {
                        "frequency": new_frequency,
                        "alert_types": new_types,
                        "digest_format": new_format
                    }
                    
                    if alert_manager.update_user_preferences(email, preferences):
                        st.success("Preferences updated successfully")
                    else:
                        st.error("Failed to update preferences")
                
                # Send test email
                if st.button("Send Test Email", key="test_settings"):
                    alert_manager.send_test_email(email)
            else:
                st.info(f"No settings found for {email}. Create an alert first to set up your profile.")
    
    # If we have investor data, show a preview section
    if investors_df is not None and not investors_df.empty:
        st.header("Alert Preview")
        st.info("See what your alert email would look like with the current search results.")
        
        email_preview = st.text_input("Enter your email for preview:")
        
        if email_preview and email_preview in alert_manager.alerts["users"]:
            user_alerts = alert_manager.get_user_alerts(email_preview)
            
            if user_alerts:
                selected_alert = st.selectbox(
                    "Select an alert to preview:",
                    user_alerts,
                    format_func=lambda x: x["name"]
                )
                
                if selected_alert:
                    # Generate preview content
                    content = alert_manager.generate_email_content(selected_alert, investors_df)
                    
                    # Show preview
                    with st.expander("Email Preview", expanded=True):
                        st.markdown(content, unsafe_allow_html=True)
            else:
                st.warning("No alerts found for this email.")
        elif email_preview:
            st.warning("Email not found. Please create an alert first.") 
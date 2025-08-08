#!/usr/bin/env python3
"""
Simplified Python Network Monitor and Alerting Tool
===================================================

This script monitors the system's public IP address and country, and triggers
an email alert and a password-protected audible alarm if a change is detected
or if the internet connection is lost/restored.

This version is designed for ethical testing and demonstration purposes only,
focusing solely on monitoring and alerting without any persistence mechanisms,
EXE conversion, image binding, or system modifications.

Author: Muhammad Arsalan Javed
Purpose: Demonstrate network monitoring and alerting techniques
Environment: Windows (requires 'winsound' for Windows-specific sound)

WARNING: This code is for authorized testing in controlled environments only.
Misuse of this code is strictly prohibited and may violate laws.
"""

import os
import sys
import time
import json
import socket
import smtplib
import threading
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import winsound # Windows-specific for sound. For other OS, use a different library.
from datetime import datetime
import logging

# Configuration
CONFIG = {
    'check_interval': 5,  # seconds between IP checks
    'retry_interval': 10,  # seconds between internet retry attempts
    'alarm_password': '123',  # Password to stop alarm
    'email_config': {
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587,
        'sender_email': 'your_email@example.com', # <<< CHANGE THIS
        'sender_password': 'your_app_password', # <<< CHANGE THIS (Use an App Password for Gmail)
        'recipient_email': 'recipient_email@example.com' # <<< CHANGE THIS
    },
    'log_file': 'network_monitor.log' # Log file in current directory
}

class NetworkMonitor:
    def __init__(self):
        self.running = True
        self.current_ip = None
        self.current_country = None
        self.alarm_active = False
        self.internet_available = self.check_internet_connection() # Initialize based on actual status
        self.email_queue = [] # Queue for pending emails
        self.initialized = False # Track if initial IP/Country have been set
        self.queue_processor_thread = threading.Thread(target=self._process_email_queue, daemon=True)
        self.queue_processor_thread.start()
        
        # Setup logging
        self.setup_logging()
        
        self.log("Network monitor initialized")

    def setup_logging(self):
        """Setup logging to file"""
        logging.basicConfig(
            filename=CONFIG['log_file'],
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def log(self, message):
        """Log message to file and print to console"""
        logging.info(message)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def check_internet_connection(self):
        """Check if internet connection is available"""
        try:
            # Try to connect to Google DNS
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

    def get_public_ip_info(self):
        """Get current public IP and country information"""
        try:
            # Primary method: ipapi.co
            response = requests.get('https://ipapi.co/json/', timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('ip'), data.get('country_name')
        except:
            pass
        
        try:
            # Fallback method: ipinfo.io
            response = requests.get('https://ipinfo.io/json', timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('ip'), data.get('country')
        except:
            pass
        
        try:
            # Second fallback: httpbin.org for IP only
            response = requests.get('https://httpbin.org/ip', timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('origin'), 'Unknown'
        except:
            pass
        
        return None, None

    def get_system_info(self):
        """Collect detailed system information"""
        try:
            import platform
            import getpass
            
            info = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'hostname': socket.gethostname(),
                'username': getpass.getuser(),
                'os_version': platform.platform(),
                'python_version': platform.python_version(),
                'ip_address': self.current_ip,
                'country': self.current_country,
                'processor': platform.processor(),
                'architecture': platform.architecture()[0]
            }
            
            return info
        except Exception as e:
            self.log(f"Error collecting system info: {e}")
            return {'error': str(e)}

    def send_alert_email(self, system_info, alert_type="Network Change"):
        """Send alert email with system information"""
        try:
            msg = MIMEMultipart()
            msg['From'] = CONFIG['email_config']['sender_email']
            msg['To'] = CONFIG['email_config']['recipient_email']
            msg['Subject'] = f"🚨 {alert_type} DETECTED - {system_info.get('hostname', 'Unknown')}"
            
            # Create email body
            body = f"""
SECURITY ALERT: {alert_type}

A {alert_type.lower()} has been detected on the monitored system.

SYSTEM INFORMATION:
==================
Timestamp: {system_info.get('timestamp', 'Unknown')}
Hostname: {system_info.get('hostname', 'Unknown')}
Username: {system_info.get('username', 'Unknown')}
Operating System: {system_info.get('os_version', 'Unknown')}
Python Version: {system_info.get('python_version', 'Unknown')}
Processor: {system_info.get('processor', 'Unknown')}
Architecture: {system_info.get('architecture', 'Unknown')}

ALERT DETAILS:
==============
"""
            
            if alert_type == "Network Change":
                body += f"Previous IP: {getattr(self, 'previous_ip', 'N/A')}\n"
                body += f"Previous Country: {getattr(self, 'previous_country', 'N/A')}\n"
                body += f"Current IP: {system_info.get('ip_address', 'Unknown')}\n"
                body += f"Current Country: {system_info.get('country', 'Unknown')}\n"
            elif alert_type == "Internet Disconnected":
                body += f"Internet connection was lost.\n"
            elif alert_type == "Internet Restored":
                body += f"Internet connection was restored.\n"
                body += f"Current IP: {system_info.get('ip_address', 'Unknown')}\n"
                body += f"Current Country: {system_info.get('country', 'Unknown')}\n"

            body += "\nThis alert was generated by the network monitoring system.\nPlease investigate immediately if this change was not authorized.\n\n---\nAutomated Security Monitoring System\n            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(CONFIG['email_config']['smtp_server'], CONFIG['email_config']['smtp_port'])
            server.starttls()
            server.login(CONFIG['email_config']['sender_email'], CONFIG['email_config']['sender_password'])
            text = msg.as_string()
            server.sendmail(CONFIG['email_config']['sender_email'], CONFIG['email_config']['recipient_email'], text)
            server.quit()
            
            self.log(f"Alert email sent successfully: {alert_type}")
            return True
            
        except Exception as e:
            self.log(f"Failed to send email ({alert_type}): {e}")
            return False

    def play_alarm_sound(self):
        """Play alarm sound continuously until stopped"""
        try:
            while self.alarm_active:
                # Play Windows system sound
                winsound.Beep(1000, 500)  # 1000 Hz for 500ms
                time.sleep(0.5)
                winsound.Beep(1500, 500)  # 1500 Hz for 500ms
                time.sleep(0.5)
        except Exception as e:
            self.log(f"Error playing alarm sound: {e}")

    def show_alarm_gui(self, alert_message):
        """Show password-protected GUI to stop alarm"""
        def stop_alarm():
            password = simpledialog.askstring("Stop Alarm", "Enter password to stop alarm:", show='*')
            if password == CONFIG['alarm_password']:
                self.alarm_active = False
                self.log("Alarm stopped by user")
                root.destroy()
            else:
                messagebox.showerror("Error", "Incorrect password!")
        
        root = tk.Tk()
        root.title("Security Alert")
        root.geometry("400x250")
        root.attributes('-topmost', True)
        
        # Make window stay on top and grab focus
        root.lift()
        root.focus_force()
        
        tk.Label(root, text="🚨 SECURITY ALERT 🚨", 
                font=("Arial", 14, "bold"), fg="red").pack(pady=10)
        
        tk.Label(root, text=alert_message, 
                font=("Arial", 10)).pack(pady=5)
        
        tk.Button(root, text="Stop Alarm", command=stop_alarm, 
                 bg="red", fg="white", font=("Arial", 12, "bold")).pack(pady=20)
        
        root.protocol("WM_DELETE_WINDOW", lambda: None)  # Disable X button
        root.mainloop()

    def trigger_alarm(self, alert_type, system_info, alert_message):
        """Trigger alarm with sound and GUI"""
        if self.alarm_active:
            return  # Alarm already active
        
        self.alarm_active = True
        self.log(f"ALARM TRIGGERED: {alert_type}")
        
        # Add email to queue
        self.email_queue.append((system_info, alert_type))
        
        # Start alarm sound in separate thread
        threading.Thread(target=self.play_alarm_sound, daemon=True).start()
        
        # Show GUI (this will block until password is entered) in separate thread
        threading.Thread(target=self.show_alarm_gui, args=(alert_message,), daemon=True).start()

    def monitor_network(self):
        """Main monitoring loop"""
        self.log("Starting network monitoring...")
        
        while self.running:
            try:
                internet_status_now = self.check_internet_connection()

                # Handle internet disconnection
                if not internet_status_now:
                    if self.internet_available: # Only trigger if it was previously available
                        self.log("Internet connection lost")
                        self.internet_available = False
                        system_info = self.get_system_info()
                        self.trigger_alarm("Internet Disconnected", system_info, "Internet connection has been lost!")
                    time.sleep(CONFIG["retry_interval"])
                    continue # Skip IP check if no internet
                
                # Handle internet restoration
                # This block will only execute if internet_status_now is True (connected)
                # and self.internet_available was False (previously disconnected)
                if not self.internet_available and internet_status_now: # This means internet_status_now is True here
                    self.internet_available = True
                    self.log("Internet connection restored")
                    # Get IP and country immediately upon restoration for accurate alert
                    ip, country = self.get_public_ip_info()
                    self.current_ip = ip
                    self.current_country = country
                    system_info = self.get_system_info() # Get system info AFTER updating IP/Country
                    self.trigger_alarm("Internet Restored", system_info, "Internet connection has been restored!")
                    self.log(f"Internet restored. Current IP: {self.current_ip}, Country: {self.current_country}")
                    # Continue to next iteration after restoration alert to avoid immediate IP change alert
                    time.sleep(CONFIG["check_interval"])
                    continue

                # Get current IP and country if internet is available
                ip, country = self.get_public_ip_info()
                
                if ip is None:
                    self.log("Failed to get IP information, retrying...")
                    time.sleep(CONFIG["check_interval"])
                    continue
                
                # Initialize current_ip and current_country on first successful IP retrieval
                # This handles the very first run where current_ip/country are None
                if not self.initialized:
                    self.current_ip = ip
                    self.current_country = country
                    self.initialized = True
                    self.log(f"Initial IP: {ip}, Country: {country}")
                    # No alarm on first run, just set initial state
                    
                # Check for changes in IP or Country (only if already initialized and internet is stable)
                elif self.current_ip != ip or self.current_country != country:
                    # Change detected
                    self.log(f"Change detected - Old: {self.current_ip}/{self.current_country}, New: {ip}/{country}")
                    
                    # Store previous values for email
                    self.previous_ip = self.current_ip
                    self.previous_country = self.current_country
                    
                    # Update current values
                    self.current_ip = ip
                    self.current_country = country
                    
                    # Trigger alarm
                    system_info = self.get_system_info()
                    alert_message = f"Network context changed!\nOld IP: {self.previous_ip}\nNew IP: {self.current_ip}\nOld Country: {self.previous_country}\nNew Country: {self.current_country}"
                    self.trigger_alarm("Network Change", system_info, alert_message)
                
                time.sleep(CONFIG['check_interval'])
                
            except KeyboardInterrupt:
                self.log("Monitoring stopped by user")
                break
            except Exception as e:
                self.log(f"Error in monitoring loop: {e}")
                time.sleep(CONFIG['retry_interval'])

    def run(self):
        """Main entry point"""
        try:
            self.monitor_network()
        except Exception as e:
            self.log(f"Fatal error: {e}")
        finally:
            self.running = False

    def _process_email_queue(self):
        """Process the email queue when internet is available"""
        while self.running:
            if self.internet_available and self.email_queue:
                system_info, alert_type = self.email_queue.pop(0) # Get the oldest email
                self.log(f"Attempting to send queued email: {alert_type}")
                if self.send_alert_email(system_info, alert_type):
                    self.log(f"Successfully sent queued email: {alert_type}")
                else:
                    self.log(f"Failed to send queued email: {alert_type}, re-queueing.")
                    self.email_queue.append((system_info, alert_type)) # Re-queue if failed
            time.sleep(5) # Check every 5 seconds

if __name__ == "__main__":
    monitor = NetworkMonitor()
    monitor.run()


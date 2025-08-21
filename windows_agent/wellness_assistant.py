"""
Wellness Assistant for StressSense Windows Agent.
A system tray application that displays stress alerts and provides wellness tips.
"""

import os
import sys
import json
import random
import logging
import sqlite3
from datetime import datetime, timedelta
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis
from windows_agent.config import ConfigManager
from windows_agent.api_client import APIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/StressSense/wellness_assistant.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Stress-relief suggestions pool
STRESS_SUGGESTIONS = {
    "Low": [
        "Take a moment to appreciate your surroundings 🌿",
        "Practice gratitude by listing 3 things you're thankful for 🙏",
        "Drink a glass of water to stay hydrated 💧",
        "Do a quick stretch at your desk 🧘‍♂️",
        "Take a short walk around your workspace 🚶‍♀️"
    ],
    "Medium": [
        "Take a 5-minute break from your screen 🕒",
        "Do some deep breathing: inhale for 4, hold for 4, exhale for 6 🌬️",
        "Step outside for fresh air if possible 🌳",
        "Roll your shoulders and stretch your neck 💆‍♂️",
        "Listen to a calming song 🎵"
    ],
    "High": [
        "Stop what you're doing and take 3 deep breaths 🧘‍♂️",
        "Step away from your desk for a short break 🚶",
        "Try the 5-4-3-2-1 grounding technique (see 5 things, hear 4 things...) 👁️",
        "Splash cold water on your face or wrists 💦",
        "Message a friend or colleague for a quick chat 💬"
    ]
}


class LocalDatabase:
    """SQLite database for storing stress data and settings locally."""
    
    def __init__(self):
        """Initialize the database."""
        self.db_path = os.path.expanduser('~/StressSense/wellness_data.db')
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Connect to the database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}", exc_info=True)
    
    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        try:
            cursor = self.conn.cursor()
            
            # Table for stress readings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stress_readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    stress_level TEXT NOT NULL,
                    emotion TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    synced INTEGER DEFAULT 0
                )
            ''')
            
            # Table for settings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')
            
            # Table for suggestions history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS suggestion_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    suggestion TEXT NOT NULL,
                    stress_level TEXT NOT NULL,
                    acknowledged INTEGER DEFAULT 0
                )
            ''')
            
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}", exc_info=True)
    
    def add_stress_reading(self, reading):
        """
        Add a stress reading to the database.
        
        Args:
            reading (dict): Stress reading data including timestamp, stress_level, emotion, confidence
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO stress_readings (timestamp, stress_level, emotion, confidence) VALUES (?, ?, ?, ?)",
                (
                    reading.get('timestamp', datetime.now().isoformat()),
                    reading.get('stress_level', 'Unknown'),
                    reading.get('emotion', 'Unknown'),
                    reading.get('confidence', 0)
                )
            )
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding stress reading: {str(e)}", exc_info=True)
            return None
    
    def get_stress_readings(self, days=7):
        """
        Get stress readings from the last N days.
        
        Args:
            days (int): Number of days to look back
            
        Returns:
            list: List of stress reading dictionaries
        """
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM stress_readings WHERE timestamp >= ? ORDER BY timestamp DESC",
                (cutoff_date,)
            )
            readings = [dict(row) for row in cursor.fetchall()]
            return readings
        except Exception as e:
            logger.error(f"Error getting stress readings: {str(e)}", exc_info=True)
            return []
    
    def get_latest_stress_reading(self):
        """
        Get the latest stress reading.
        
        Returns:
            dict: Latest stress reading or None if no readings exist
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM stress_readings ORDER BY timestamp DESC LIMIT 1")
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting latest stress reading: {str(e)}", exc_info=True)
            return None
    
    def add_suggestion_history(self, suggestion, stress_level):
        """
        Add a suggestion to history.
        
        Args:
            suggestion (str): The suggestion text
            stress_level (str): The stress level (Low, Medium, High)
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO suggestion_history (timestamp, suggestion, stress_level) VALUES (?, ?, ?)",
                (datetime.now().isoformat(), suggestion, stress_level)
            )
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding suggestion history: {str(e)}", exc_info=True)
            return None
    
    def mark_suggestion_acknowledged(self, suggestion_id):
        """Mark a suggestion as acknowledged."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE suggestion_history SET acknowledged = 1 WHERE id = ?",
                (suggestion_id,)
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error marking suggestion acknowledged: {str(e)}", exc_info=True)
    
    def get_setting(self, key, default=None):
        """Get a setting value."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row['value'] if row else default
        except Exception as e:
            logger.error(f"Error getting setting: {str(e)}", exc_info=True)
            return default
    
    def set_setting(self, key, value):
        """Set a setting value."""
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value)
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error setting setting: {str(e)}", exc_info=True)
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()


class StressNotifier(QtCore.QObject):
    """Monitors stress readings and shows notifications."""
    
    new_reading_signal = QtCore.pyqtSignal(dict)
    
    def __init__(self, db, parent=None):
        """Initialize the notifier."""
        super().__init__(parent)
        self.db = db
        self.last_notification_time = None
        self.notification_cooldown = 60 * 10  # 10 minutes in seconds
    
    def check_stress_level(self, reading):
        """
        Check stress level and notify if needed.
        
        Args:
            reading (dict): Stress reading data
        """
        # Save reading to database
        self.db.add_stress_reading(reading)
        
        # Emit signal for UI update
        self.new_reading_signal.emit(reading)
        
        stress_level = reading.get('stress_level')
        if not stress_level or stress_level == 'Low':
            return None  # No need to notify for low stress
        
        # Check if we should show notification based on cooldown
        current_time = datetime.now()
        if (self.last_notification_time is not None and 
            (current_time - self.last_notification_time).total_seconds() < self.notification_cooldown):
            return None
        
        # Get a random suggestion for this stress level
        suggestion = random.choice(STRESS_SUGGESTIONS.get(stress_level, STRESS_SUGGESTIONS['Medium']))
        
        # Save suggestion to history
        suggestion_id = self.db.add_suggestion_history(suggestion, stress_level)
        
        # Update last notification time
        self.last_notification_time = current_time
        
        return {
            'id': suggestion_id,
            'title': f"Stress Alert {'🔶' if stress_level == 'Medium' else '🔴'}",
            'message': suggestion,
            'level': stress_level
        }


class DashboardWindow(QtWidgets.QMainWindow):
    """Main dashboard window for the wellness assistant."""
    
    def __init__(self, db, parent=None):
        """Initialize the dashboard window."""
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("StressSense Wellness Dashboard")
        self.resize(800, 600)
        self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), 'assets/icon.png')))
        
        # Create tabs
        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Add tabs
        self.overview_tab = self._create_overview_tab()
        self.history_tab = self._create_history_tab()
        self.suggestions_tab = self._create_suggestions_tab()
        
        self.tabs.addTab(self.overview_tab, "Overview")
        self.tabs.addTab(self.history_tab, "History")
        self.tabs.addTab(self.suggestions_tab, "Suggestions")
        
        # Set up periodic refresh
        self.refresh_timer = QtCore.QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(60000)  # Refresh every minute
        
        # Initial data load
        self.refresh_data()
    
    def _create_overview_tab(self):
        """Create the overview tab."""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        tab.setLayout(layout)
        
        # Header
        header_layout = QtWidgets.QHBoxLayout()
        welcome_label = QtWidgets.QLabel("Wellness Dashboard")
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(welcome_label)
        header_layout.addStretch(1)
        
        refresh_btn = QtWidgets.QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Status card
        self.status_card = QtWidgets.QGroupBox("Current Stress Level")
        status_layout = QtWidgets.QVBoxLayout()
        self.status_card.setLayout(status_layout)
        
        # Status content
        self.level_label = QtWidgets.QLabel("Level: Unknown")
        self.level_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        status_layout.addWidget(self.level_label)
        
        self.emotion_label = QtWidgets.QLabel("Emotion: Unknown")
        status_layout.addWidget(self.emotion_label)
        
        self.confidence_label = QtWidgets.QLabel("Confidence: 0%")
        status_layout.addWidget(self.confidence_label)
        
        self.timestamp_label = QtWidgets.QLabel("Last updated: Never")
        self.timestamp_label.setStyleSheet("color: gray;")
        status_layout.addWidget(self.timestamp_label)
        
        layout.addWidget(self.status_card)
        
        # Quick tips card
        self.tips_card = QtWidgets.QGroupBox("Wellness Tip")
        tips_layout = QtWidgets.QVBoxLayout()
        self.tips_card.setLayout(tips_layout)
        
        self.tip_label = QtWidgets.QLabel("Take a moment to breathe deeply")
        self.tip_label.setWordWrap(True)
        self.tip_label.setStyleSheet("font-size: 16px;")
        tips_layout.addWidget(self.tip_label)
        
        new_tip_btn = QtWidgets.QPushButton("New Tip")
        new_tip_btn.clicked.connect(self._generate_new_tip)
        tips_layout.addWidget(new_tip_btn)
        
        layout.addWidget(self.tips_card)
        
        # Add spacer
        layout.addStretch(1)
        
        return tab
    
    def _create_history_tab(self):
        """Create the history tab."""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        tab.setLayout(layout)
        
        # History chart
        chart_group = QtWidgets.QGroupBox("Stress Level History (Last 7 Days)")
        chart_layout = QtWidgets.QVBoxLayout()
        chart_group.setLayout(chart_layout)
        
        # Create chart
        self.chart = QChart()
        self.chart.setTitle("Stress Level History")
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(QtCore.Qt.AlignBottom)
        
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QtGui.QPainter.Antialiasing)
        chart_layout.addWidget(self.chart_view)
        
        layout.addWidget(chart_group)
        
        # Controls
        controls_layout = QtWidgets.QHBoxLayout()
        
        days_label = QtWidgets.QLabel("Show data for:")
        controls_layout.addWidget(days_label)
        
        self.days_combo = QtWidgets.QComboBox()
        self.days_combo.addItems(["Last 7 days", "Last 14 days", "Last 30 days"])
        self.days_combo.currentIndexChanged.connect(self._update_history_days)
        controls_layout.addWidget(self.days_combo)
        
        controls_layout.addStretch(1)
        
        refresh_btn = QtWidgets.QPushButton("Refresh Chart")
        refresh_btn.clicked.connect(self._update_chart)
        controls_layout.addWidget(refresh_btn)
        
        layout.addLayout(controls_layout)
        
        # Add spacer
        layout.addStretch(1)
        
        return tab
    
    def _create_suggestions_tab(self):
        """Create the suggestions tab."""
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        tab.setLayout(layout)
        
        # Header
        header = QtWidgets.QLabel("Stress Relief Techniques")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)
        
        # Create scrollable area for suggestions
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QtWidgets.QWidget()
        self.suggestions_layout = QtWidgets.QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # Categories
        categories = ["When stress is low", "When stress is moderate", "When stress is high"]
        
        for i, category in enumerate(categories):
            level = ["Low", "Medium", "High"][i]
            
            # Add category header
            category_label = QtWidgets.QLabel(category)
            category_label.setStyleSheet("font-weight: bold; font-size: 16px;")
            self.suggestions_layout.addWidget(category_label)
            
            # Add suggestions for this category
            for suggestion in STRESS_SUGGESTIONS[level]:
                suggestion_item = QtWidgets.QLabel(f"• {suggestion}")
                suggestion_item.setWordWrap(True)
                suggestion_item.setStyleSheet("padding-left: 20px;")
                self.suggestions_layout.addWidget(suggestion_item)
            
            # Add spacing between categories
            self.suggestions_layout.addSpacing(20)
        
        # Add spacer
        self.suggestions_layout.addStretch(1)
        
        return tab
    
    def refresh_data(self):
        """Refresh all data in the dashboard."""
        # Update overview tab
        self._update_status_card()
        
        # Update history tab
        self._update_chart()
    
    def _update_status_card(self):
        """Update the status card with latest stress data."""
        latest = self.db.get_latest_stress_reading()
        
        if not latest:
            return
        
        # Update labels
        self.level_label.setText(f"Level: {latest['stress_level']}")
        
        # Set color based on stress level
        if latest['stress_level'] == 'Low':
            self.level_label.setStyleSheet("font-size: 18px; font-weight: bold; color: green;")
        elif latest['stress_level'] == 'Medium':
            self.level_label.setStyleSheet("font-size: 18px; font-weight: bold; color: orange;")
        else:  # High
            self.level_label.setStyleSheet("font-size: 18px; font-weight: bold; color: red;")
        
        self.emotion_label.setText(f"Emotion: {latest['emotion']}")
        self.confidence_label.setText(f"Confidence: {int(latest['confidence'])}%")
        
        # Format timestamp
        try:
            timestamp = datetime.fromisoformat(latest['timestamp'])
            formatted_time = timestamp.strftime("%b %d, %Y at %I:%M %p")
            self.timestamp_label.setText(f"Last updated: {formatted_time}")
        except:
            self.timestamp_label.setText(f"Last updated: {latest['timestamp']}")
    
    def _generate_new_tip(self):
        """Generate a new random tip."""
        # Get latest stress level or default to medium
        latest = self.db.get_latest_stress_reading()
        level = latest['stress_level'] if latest else 'Medium'
        
        # Get a random suggestion
        suggestion = random.choice(STRESS_SUGGESTIONS[level])
        self.tip_label.setText(suggestion)
    
    def _update_history_days(self):
        """Update the number of days to show in history."""
        self._update_chart()
    
    def _update_chart(self):
        """Update the stress history chart."""
        # Determine days to show
        days_index = self.days_combo.currentIndex()
        days = [7, 14, 30][days_index]
        
        # Get data
        readings = self.db.get_stress_readings(days=days)
        
        # Clear existing series
        self.chart.removeAllSeries()
        
        # Create new series
        series = QLineSeries()
        series.setName("Stress Level")
        
        # Map stress levels to numeric values
        stress_map = {"Low": 1, "Medium": 2, "High": 3, "Unknown": 0}
        
        # Add data points
        for reading in sorted(readings, key=lambda x: x['timestamp']):
            try:
                timestamp = datetime.fromisoformat(reading['timestamp'])
                ms_since_epoch = int(timestamp.timestamp() * 1000)
                stress_value = stress_map.get(reading['stress_level'], 0)
                
                series.append(ms_since_epoch, stress_value)
            except:
                continue
        
        self.chart.addSeries(series)
        
        # Create X axis (time)
        axis_x = QDateTimeAxis()
        axis_x.setFormat("MMM d")
        axis_x.setTitleText("Date")
        self.chart.addAxis(axis_x, QtCore.Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        # Create Y axis (stress level)
        axis_y = QValueAxis()
        axis_y.setRange(0, 4)
        axis_y.setTickCount(4)
        axis_y.setLabelFormat("%d")
        self.chart.addAxis(axis_y, QtCore.Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        # Custom Y axis labels
        labels = ["", "Low", "Medium", "High"]
        for i in range(1, 4):
            label = QtWidgets.QGraphicsSimpleTextItem(self.chart)
            label.setText(labels[i])
            x_min = axis_x.min().toMSecsSinceEpoch() if hasattr(axis_x.min(), 'toMSecsSinceEpoch') else 0
            label.setPos(self.chart.mapToPosition(QtCore.QPointF(x_min, i)))


class SystemTrayApp(QtWidgets.QSystemTrayIcon):
    """System tray application for the wellness assistant."""
    
    def __init__(self, parent=None):
        """Initialize the system tray app."""
        super().__init__(parent)
        self.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), 'assets/icon.png')))
        self.setToolTip("StressSense Wellness Assistant")
        
        # Initialize database
        self.db = LocalDatabase()
        
        # Initialize stress notifier
        self.notifier = StressNotifier(self.db)
        self.notifier.new_reading_signal.connect(self.on_new_reading)
        
        # Initialize API client
        self.config_manager = ConfigManager()
        self.api_client = APIClient(self.config_manager)
        
        # Create dashboard window
        self.dashboard = DashboardWindow(self.db)
        
        # Create context menu
        self.setup_menu()
        
        # Connect signals
        self.activated.connect(self.on_tray_activated)
        
        # Show the tray icon
        self.show()
        
        # Initial message
        self.showMessage(
            "StressSense Wellness Assistant",
            "Your wellness assistant is now running in the background.",
            QtWidgets.QSystemTrayIcon.Information,
            5000
        )
        
        # Start background sync
        self.sync_timer = QtCore.QTimer()
        self.sync_timer.timeout.connect(self.sync_with_backend)
        self.sync_timer.start(60000 * 5)  # Every 5 minutes
        
        # Initial sync
        QtCore.QTimer.singleShot(5000, self.sync_with_backend)
    
    def setup_menu(self):
        """Set up the context menu."""
        menu = QtWidgets.QMenu()
        
        # Open dashboard action
        open_action = menu.addAction("Open Dashboard")
        open_action.triggered.connect(self.open_dashboard)
        
        # Sync action
        sync_action = menu.addAction("Sync Data")
        sync_action.triggered.connect(self.sync_with_backend)
        
        # Separator
        menu.addSeparator()
        
        # Check now action
        check_action = menu.addAction("Check Stress Now")
        check_action.triggered.connect(self.trigger_stress_check)
        
        # Separator
        menu.addSeparator()
        
        # Exit action
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.exit_app)
        
        self.setContextMenu(menu)
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QtWidgets.QSystemTrayIcon.DoubleClick:
            self.open_dashboard()
    
    def open_dashboard(self):
        """Open the dashboard window."""
        self.dashboard.refresh_data()
        self.dashboard.show()
        self.dashboard.raise_()
        self.dashboard.activateWindow()
    
    def sync_with_backend(self):
        """Sync data with the backend."""
        try:
            # Fetch latest stress data from backend
            result = self.api_client.get_employee_stress_history()
            
            if not result or not result.get('success'):
                logger.warning(f"Failed to fetch stress history from backend: {result.get('message', 'Unknown error')}")
                return
            
            # Process and store readings
            history = result.get('data', [])
            for reading in history:
                self.process_stress_reading(reading)
                
            logger.info(f"Synced {len(history)} readings from backend")
        except Exception as e:
            logger.error(f"Error syncing with backend: {str(e)}", exc_info=True)
    
    def on_new_reading(self, reading):
        """Handle new stress reading."""
        # Update dashboard if it's open
        if self.dashboard.isVisible():
            self.dashboard.refresh_data()
    
    def process_stress_reading(self, reading):
        """
        Process a stress reading from the backend or agent.
        
        Args:
            reading (dict): The stress reading data
        """
        # Check for required fields
        if 'timestamp' not in reading or 'stress_level' not in reading:
            logger.warning("Ignoring invalid stress reading (missing required fields)")
            return
        
        # Store in local database
        self.db.add_stress_reading(reading)
        
        # Check if we need to notify
        notification = self.notifier.check_stress_level(reading)
        if notification:
            self.showMessage(
                notification['title'],
                notification['message'],
                QtWidgets.QSystemTrayIcon.Warning,
                10000  # 10 seconds
            )
    
    def trigger_stress_check(self):
        """Trigger an immediate stress check."""
        try:
            # Request the agent to check stress
            device_id = self.config_manager.get_secure_data().get('device_id')
            if not device_id:
                self.showMessage(
                    "Error",
                    "Device not registered. Please register the device first.",
                    QtWidgets.QSystemTrayIcon.Warning
                )
                return
                
            result = self.api_client.trigger_analyze_now()
            
            if result and result.get('success'):
                self.showMessage(
                    "Stress Check",
                    "Stress check has been triggered. Results will appear shortly.",
                    QtWidgets.QSystemTrayIcon.Information
                )
            else:
                self.showMessage(
                    "Error",
                    f"Failed to trigger stress check: {result.get('message', 'Unknown error')}",
                    QtWidgets.QSystemTrayIcon.Warning
                )
        except Exception as e:
            logger.error(f"Error triggering stress check: {str(e)}", exc_info=True)
            self.showMessage(
                "Error",
                f"Failed to trigger stress check: {str(e)}",
                QtWidgets.QSystemTrayIcon.Warning
            )
    
    def exit_app(self):
        """Exit the application."""
        # Close database
        self.db.close()
        
        # Quit application
        QtWidgets.QApplication.quit()


def run():
    """Run the wellness assistant."""
    # Check if already running
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("StressSense Wellness Assistant")
    app.setQuitOnLastWindowClosed(False)
    
    # Create system tray app
    tray = SystemTrayApp()
    
    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()

import sys
from PyQt6.QtCore import QUrl, Qt, QTimer, QSize
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                           QVBoxLayout, QLineEdit, QHBoxLayout,
                           QPushButton, QFrame, QLabel, QListWidget)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QColor, QPalette, QFont, QIcon, QPainter
from urllib.parse import urlparse
from astradb_access import get_template_by_url
import pygame
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import random
import os
from pathlib import Path
from extract_template import generate_personalized_content
from PyQt6.QtCore import QPropertyAnimation, QPoint, QEasingCurve
from podcast_talk import PodcastTalk

# Create a constant for the podcasts directory
PODCASTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'podcasts')
# Create the podcasts directory if it doesn't exist
os.makedirs(PODCASTS_DIR, exist_ok=True)

class ModernUrlBar(QLineEdit):
    def __init__(self):
        super().__init__()
        # Set modern styling for URL bar
        self.setFixedHeight(45)  # Make it taller
        self.setFont(QFont('Arial', 12))
        self.setStyleSheet('''
            QLineEdit {
                background-color: #2A2A2A;
                border: 2px solid #2A2A2A;
                border-radius: 22px;
                padding: 0 15px;
                color: #FFFFFF;
                selection-background-color: #404040;
            }
            QLineEdit:focus {
                border: 2px solid #404040;
                background-color: #333333;
            }
        ''')
        self.setPlaceholderText('Enter URL here (e.g., https://www.google.com)')

class PodcastPlayer(QMainWindow):
    def __init__(self, podcast_name):
        super().__init__()
        self.setWindowTitle(f'Playing: {podcast_name}')
        self.setGeometry(200, 200, 800, 400)
        
        # Store podcast info
        self.podcast_name = podcast_name
        self.mp3_path = os.path.join(PODCASTS_DIR, f"{podcast_name}.mp3")
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Add status label
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        
        # Style
        self.setStyleSheet('''
            QMainWindow, QWidget {
                background-color: #1A1A1A;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #2A2A2A;
                border: none;
                border-radius: 15px;
                padding: 10px 20px;
                color: #FFFFFF;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #404040;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 16px;
            }
        ''')
        
        # Title
        self.title_label = QLabel(podcast_name)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Matplotlib Figure for waveform
        self.figure = Figure(facecolor='#1A1A1A')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#1A1A1A')
        self.figure.patch.set_facecolor('#1A1A1A')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        layout.addWidget(self.canvas)
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.play_button = QPushButton('Play')
        self.stop_button = QPushButton('Stop')
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.stop_button)
        layout.addLayout(button_layout)
        
        # Connect buttons
        self.play_button.clicked.connect(self.play_audio)
        self.stop_button.clicked.connect(self.stop_audio)
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Timer for updating waveform
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_waveform)
        
        # Generate sample waveform data
        self.waveform_data = np.random.rand(1000) * 2 - 1
        self.current_frame = 0
        self.is_playing = False
        
        # Check if MP3 exists
        self.check_mp3_exists()
        
        # Initial waveform plot
        self.plot_waveform()
        
    def check_mp3_exists(self):
        if not os.path.exists(self.mp3_path):
            self.status_label.setText(f"Please place MP3 file at:\n{self.mp3_path}")
            self.play_button.setEnabled(False)
        else:
            self.status_label.setText("MP3 file found!")
            self.play_button.setEnabled(True)
        
    def play_audio(self):
        if not self.is_playing and os.path.exists(self.mp3_path):
            try:
                pygame.mixer.music.load(self.mp3_path)
                pygame.mixer.music.play()
                self.is_playing = True
                self.timer.start(50)  # Update every 50ms
                self.status_label.setText("Playing...")
            except Exception as e:
                self.status_label.setText(f"Error playing file: {str(e)}")
            
    def stop_audio(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.timer.stop()
        self.current_frame = 0
        self.plot_waveform()
        self.status_label.setText("Stopped")
        
    def plot_waveform(self):
        self.ax.clear()
        self.ax.plot(self.waveform_data[:self.current_frame], color='#00FF00', linewidth=1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_xlim(0, 1000)
        self.ax.grid(True, color='#333333')
        self.canvas.draw()
        
    def update_waveform(self):
        if self.is_playing:
            self.current_frame = (self.current_frame + 10) % 1000
            self.plot_waveform()

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Create loading indicator
        self.loading_label = QLabel("⭐", self)
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 48px;
                background: transparent;
            }
        """)
        self.loading_label.setFixedSize(50, 50)
        
        # Create loading text
        self.text_label = QLabel("Loading...", self)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 16px;
                background: transparent;
            }
        """)
        self.text_label.move(75, 120)
        
        # Setup rotation animation
        self.animation = QPropertyAnimation(self.loading_label, b"pos")
        self.animation.setDuration(2000)
        self.animation.setStartValue(QPoint(75, 50))
        self.animation.setEndValue(QPoint(75, 50))
        self.animation.setLoopCount(-1)  # Infinite loop
        
        # Create circular motion
        steps = 60
        for i in range(steps + 1):
            angle = (i / steps) * 2 * 3.14159
            radius = 30
            x = 75 + radius * np.cos(angle)
            y = 50 + radius * np.sin(angle)
            self.animation.setKeyValueAt(i/steps, QPoint(int(x), int(y)))
        
        self.animation.setEasingCurve(QEasingCurve.Type.Linear)
        
    def showEvent(self, event):
        super().showEvent(event)
        self.animation.start()
        
    def hideEvent(self, event):
        super().hideEvent(event)
        self.animation.stop()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(0, 0, 0, 180))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 10, 10)

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Modern Web Browser')
        self.setGeometry(100, 100, 1400, 800)
        
        # Set the window background color
        self.setStyleSheet('''
            QMainWindow {
                background-color: #1A1A1A;
            }
            QWidget {
                background-color: #1A1A1A;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: #2A2A2A;
                border-radius: 10px;
            }
            QListWidget {
                background-color: #2A2A2A;
                border-radius: 10px;
                color: #FFFFFF;
                padding: 10px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 5px;
            }
            QListWidget::item:hover {
                background-color: #404040;
            }
        ''')

        # Create central widget and main horizontal layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Left column for browser (70% of width)
        browser_column = QWidget()
        browser_layout = QVBoxLayout(browser_column)
        browser_layout.setSpacing(10)
        browser_layout.setContentsMargins(0, 0, 0, 0)

        # Create top bar container
        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)
        top_layout.setSpacing(10)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Create navigation buttons
        nav_buttons_style = '''
            QPushButton {
                background-color: #2A2A2A;
                border: none;
                border-radius: 15px;
                padding: 8px;
                color: #FFFFFF;
                min-width: 30px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #404040;
            }
            QPushButton:pressed {
                background-color: #505050;
            }
            QPushButton:disabled {
                background-color: #1A1A1A;
                color: #666666;
            }
        '''
        
        # Back button
        self.back_button = QPushButton("←")
        self.back_button.setStyleSheet(nav_buttons_style)
        self.back_button.clicked.connect(lambda: self.web_view.back())
        
        # Forward button
        self.forward_button = QPushButton("→")
        self.forward_button.setStyleSheet(nav_buttons_style)
        self.forward_button.clicked.connect(lambda: self.web_view.forward())
        
        # Refresh button
        self.refresh_button = QPushButton("↻")
        self.refresh_button.setStyleSheet(nav_buttons_style)
        self.refresh_button.clicked.connect(lambda: self.web_view.reload())

        # Add navigation buttons to top layout
        top_layout.addWidget(self.back_button)
        top_layout.addWidget(self.forward_button)
        top_layout.addWidget(self.refresh_button)

        # Create modern URL bar
        self.url_bar = ModernUrlBar()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        top_layout.addWidget(self.url_bar)

        # Add top bar to browser layout
        browser_layout.addWidget(top_bar)

        # Create web view with modern styling
        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl('https://www.google.com'))
        self.web_view.setStyleSheet('''
            QWebEngineView {
                background-color: #FFFFFF;
                border-radius: 10px;
            }
        ''')
        browser_layout.addWidget(self.web_view)

        # Right column (30% of width)
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.setSpacing(20)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Podcasts section
        podcasts_section = QWidget()
        podcasts_layout = QVBoxLayout(podcasts_section)
        podcasts_label = QLabel("Podcasts")
        self.podcasts_list = QListWidget()
        
        # Get list of available podcasts from the podcasts directory
        available_podcasts = self.get_available_podcasts()
        self.podcasts_list.addItems(available_podcasts)
        
        self.podcasts_list.itemClicked.connect(self.open_podcast_player)
        podcasts_layout.addWidget(podcasts_label)
        podcasts_layout.addWidget(self.podcasts_list)

        # Chat/Call section
        chat_section = QWidget()
        chat_layout = QVBoxLayout(chat_section)
        chat_label = QLabel("Chat / Call")
        chat_list = QListWidget()
        chat_list.addItems(["📱 John Smith", "💬 Alice Johnson", "📱 Bob Wilson", "💬 Emma Davis"])
        chat_layout.addWidget(chat_label)
        chat_layout.addWidget(chat_list)

        # Add sections to right column
        right_layout.addWidget(podcasts_section)
        right_layout.addWidget(chat_section)

        # Add columns to main layout with stretch factors
        main_layout.addWidget(browser_column, stretch=70)
        main_layout.addWidget(right_column, stretch=30)

        # Connect web view signals
        self.web_view.urlChanged.connect(self.update_url_bar)
        self.web_view.loadStarted.connect(lambda: self.refresh_button.setEnabled(False))
        self.web_view.loadFinished.connect(lambda: self.refresh_button.setEnabled(True))

        # Add loading overlay
        self.loading_overlay = LoadingOverlay(self.web_view)
        self.loading_overlay.hide()

    def showLoading(self):
        self.loading_overlay.move(
            (self.web_view.width() - self.loading_overlay.width()) // 2,
            (self.web_view.height() - self.loading_overlay.height()) // 2
        )
        self.loading_overlay.show()
        
    def hideLoading(self):
        self.loading_overlay.hide()

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Extract domain from URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        if domain.startswith('www.'):
            domain = domain[4:]
            
        # Show loading overlay
        self.showLoading()
        
        # Check if domain exists in AstraDB
        cached_data = None
        for i in range(0,3):
            try:
                cached_data = get_template_by_url(domain)
                break
            except:
                continue
        
        if cached_data and 'template' in cached_data:
            # Save template to a temporary file
            temp_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_template.html')
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(cached_data['template'])
            
            # Hardcoded personality traits for now
            personality_traits = """Happiness: 8/10
            Excitement: 7/10
            Sarcasm: 3/10
            Professionalism: 9/10
            Humor: 6/10"""
            
            # Generate personalized content
            generated_file = generate_personalized_content(temp_file, personality_traits)
            
            if generated_file:
                # Read the generated file and display it
                with open(generated_file, 'r', encoding='utf-8') as f:
                    generated_html = f.read()
                self.web_view.setHtml(generated_html)
                
                # Clean up temporary files
                try:
                    os.remove(temp_file)
                    os.remove(generated_file)
                except:
                    pass
            else:
                # Fallback to original template if generation fails
                self.web_view.setHtml(cached_data['template'])
            
            self.url_bar.setText(url)
            self.url_bar.setCursorPosition(0)
        else:
            # If no template exists, load the actual webpage
            self.web_view.setUrl(QUrl(url))
            
        # Hide loading overlay
        self.hideLoading()

    def update_url_bar(self, url):
        self.url_bar.setText(url.toString())
        self.url_bar.setCursorPosition(0)

    def open_podcast_player(self, item):
        podcast_name = item.text()
        self.podcast_player = PodcastPlayer(podcast_name)
        self.podcast_player.show()

    def get_available_podcasts(self):
        # Default podcasts if no MP3s found
        default_podcasts = ["Echo Chamber Podcast"]
        
        # Get actual MP3 files from the podcasts directory
        try:
            mp3_files = [f.stem for f in Path(PODCASTS_DIR).glob("*.mp3")]
            return mp3_files if mp3_files else default_podcasts
        except Exception:
            return default_podcasts

def main():
    # Enable high DPI scaling - using updated attribute names
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    #QApplication.setAttribute(Qt.ApplicationAttribute.UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    
    # Set application-wide dark theme
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(26, 26, 26))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
    palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    app.setPalette(palette)
    podcast_talk = PodcastTalk()
    podcast_talk.generate_podcast("neutral-sad-talks")
    podcast_talk.merge_clips(podcast_talk.generate_talk())
    
    browser = Browser()
    browser.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 
import sys
from PyQt6.QtCore import QUrl, Qt, QTimer
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                           QVBoxLayout, QLineEdit, QHBoxLayout,
                           QPushButton, QFrame, QLabel, QListWidget)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QColor, QPalette, QFont, QIcon
from urllib.parse import urlparse
from astradb_access import get_template_by_url
import pygame
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import random
import os
#from PyQt6.QtWebEngineCore import QWebEngineHttpHandler

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
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
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
        
        # Initial waveform plot
        self.plot_waveform()
        
    def plot_waveform(self):
        self.ax.clear()
        self.ax.plot(self.waveform_data[:self.current_frame], color='#00FF00', linewidth=1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_xlim(0, 1000)
        self.ax.grid(True, color='#333333')
        self.canvas.draw()
        
    def play_audio(self):
        if not self.is_playing:
            # For demonstration, we'll just play a simple beep sound
            frequency = 440  # Hz
            duration = 1000  # ms
            pygame.mixer.Sound(np.sin(2 * np.pi * np.arange(44100) * frequency / 44100).astype(np.float32)).play()
            self.is_playing = True
            self.timer.start(50)  # Update every 50ms
            
    def stop_audio(self):
        pygame.mixer.stop()
        self.is_playing = False
        self.timer.stop()
        self.current_frame = 0
        self.plot_waveform()
        
    def update_waveform(self):
        if self.is_playing:
            self.current_frame = (self.current_frame + 10) % 1000
            self.plot_waveform()

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
        self.podcasts_list.addItems(["Tech Talk Daily", "Code Chronicles", "Dev Discussion", "Python Pioneers"])
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

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        # Extract domain from URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        if domain.startswith('www.'):
            domain = domain[4:]

        # Check if domain exists in AstraDB
        for i in range(0,3):
            try:
                cached_data = get_template_by_url(domain)
            except:
                continue
        
        if cached_data and 'template' in cached_data:
            # If template exists, load it directly into the web view
            self.web_view.setHtml(cached_data['template'])
            self.url_bar.setText(url)
            self.url_bar.setCursorPosition(0)
        else:
            # If no template exists, load the actual webpage
            self.web_view.setUrl(QUrl(url))

    def update_url_bar(self, url):
        self.url_bar.setText(url.toString())
        self.url_bar.setCursorPosition(0)

    def open_podcast_player(self, item):
        podcast_name = item.text()
        self.podcast_player = PodcastPlayer(podcast_name)
        self.podcast_player.show()

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
    
    browser = Browser()
    browser.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 
import sys
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
                           QVBoxLayout, QLineEdit, QHBoxLayout,
                           QPushButton, QFrame)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QColor, QPalette, QFont, QIcon
from urllib.parse import urlparse
from astradb_access import get_template_by_url
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

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Modern Web Browser')
        self.setGeometry(100, 100, 1200, 800)
        
        # Set the window background color
        self.setStyleSheet('''
            QMainWindow {
                background-color: #1A1A1A;
            }
            QWidget {
                background-color: #1A1A1A;
            }
        ''')

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)

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

        # Add top bar to main layout
        main_layout.addWidget(top_bar)

        # Create web view with modern styling
        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl('https://www.google.com'))
        self.web_view.setStyleSheet('''
            QWebEngineView {
                background-color: #FFFFFF;
                border-radius: 10px;
            }
        ''')
        main_layout.addWidget(self.web_view)

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
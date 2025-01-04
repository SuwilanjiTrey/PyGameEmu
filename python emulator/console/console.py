import sys
import os
import importlib.util
import sqlite3
import subprocess
import cv2
import numpy as np
import psutil
import pygame

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                             QMenuBar, QMenu, QAction, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap

class VideoThread(QThread):
    """Handles video playback in a separate thread"""
    update_frame = pyqtSignal(QImage)

    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.running = True

    def run(self):
        cap = cv2.VideoCapture(self.video_path)
        while self.running:
            ret, frame = cap.read()
            if not ret:
                # Reset to the beginning of the video when it ends
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            
            self.update_frame.emit(qt_image)
            self.msleep(33)  # ~30 FPS

        cap.release()

    def stop(self):
        self.running = False

class MenuDrawer(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(250)
        self.setup_ui()
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-right: 1px solid #3d3d3d;
            }
            QPushButton {
                background-color: #3d3d3d;
                color: white;
                border: none;
                padding: 8px;
                margin: 2px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QLabel {
                color: white;
                padding: 8px;
            }
        """)
        
    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Title
        title = QLabel("Menu")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Add More Games button
        self.add_games_btn = QPushButton("➕ Add More Games")
        layout.addWidget(self.add_games_btn)
        
        # Settings section
        settings_label = QLabel("Settings")
        settings_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 20px;")
        layout.addWidget(settings_label)
        
        self.keyboard_btn = QPushButton("⌨️ Keyboard Config")
        self.joystick_btn = QPushButton("🎮 Joystick Config")
        self.debug_btn = QPushButton("🐛 Debug Mode")
        
        layout.addWidget(self.keyboard_btn)
        layout.addWidget(self.joystick_btn)
        layout.addWidget(self.debug_btn)
        
        layout.addStretch()

class GameConsole(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyGame Game Console")
        self.resize(1200, 900)

        # Core configuration
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_folder = os.path.join(self.base_dir, "config")
        self.db_folder = os.path.join(self.config_folder, "db")
        
        # Ensure config directories exist
        os.makedirs(self.config_folder, exist_ok=True)
        os.makedirs(self.db_folder, exist_ok=True)

        # Initialize game state
        self.current_game = None
        self.current_process = None
        self.debug_active = False

        # Initialize pygame for joystick support
        pygame.init()
        pygame.joystick.init()

        # Setup UI
        self.setup_ui()
        self.setup_menus()

        # Start background video
        self.start_background_video()

    def setup_ui(self):
        """Create the main user interface"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main horizontal layout
        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        
        # Add menu drawer (hidden by default)
        self.menu_drawer = MenuDrawer(self)
        self.menu_drawer.hide()
        self.main_layout.addWidget(self.menu_drawer)
        
        # Content area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_widget.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_widget)
        
        # Video background
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.video_label)

        # Game frame
        self.game_frame = QWidget()
        self.game_frame.setLayout(QVBoxLayout())
        self.content_layout.addWidget(self.game_frame)
        
        # Connect drawer buttons
        self.menu_drawer.add_games_btn.clicked.connect(self.load_game)
        self.menu_drawer.keyboard_btn.clicked.connect(self.open_keyboard_config)
        self.menu_drawer.joystick_btn.clicked.connect(self.open_joystick_config)
        self.menu_drawer.debug_btn.clicked.connect(self.toggle_debug)

    def setup_menus(self):
        """Create application menus"""
        self.menu_bar = self.menuBar()
        
        # Menu button
        menu_action = QAction("☰ Menu", self)
        menu_action.triggered.connect(self.toggle_menu)
        self.menu_bar.addAction(menu_action)

    def toggle_menu(self):
        """Toggle the menu drawer"""
        if self.menu_drawer.isHidden():
            self.menu_drawer.show()
        else:
            self.menu_drawer.hide()

    def start_background_video(self):
        # Optional: Set a default background image
        default_bg_path = os.path.join(self.base_dir, 'config', 'img', 'background.png')
        if os.path.exists(default_bg_path):
            pixmap = QPixmap(default_bg_path)
            scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.video_label.setPixmap(scaled_pixmap)

    def update_video_frame(self, qt_image):
        """Update video frame on UI"""
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(scaled_pixmap)

    def load_game(self):
        """Load a game from file"""
        game_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Game", 
            "", 
            "Python Files (*.py)"
        )
        
        if game_path:
            self.run_game(game_path)

    def run_game(self, game_path):
        """Run the selected game module"""
        # Clean up previous game frame
        for i in reversed(range(self.game_frame.layout().count())): 
            self.game_frame.layout().itemAt(i).widget().setParent(None)

        # Import the game module dynamically
        spec = importlib.util.spec_from_file_location("game_module", game_path)
        game_module = importlib.util.module_from_spec(spec)
        sys.modules["game_module"] = game_module
        spec.loader.exec_module(game_module)

        # Run the game if it has a run method
        if hasattr(game_module, 'run'):
            game_module.run(self.game_frame)
        else:
            QMessageBox.warning(self, "Error", "The game module doesn't have a 'run' function.")

        self.current_game = game_path

    def open_keyboard_config(self):
        """Open keyboard configuration"""
        self.close_current_process()
        keyboard_config_path = os.path.join(self.config_folder, "keyboardConfig.py")
        
        if os.path.exists(keyboard_config_path):
            self.current_process = subprocess.Popen([sys.executable, keyboard_config_path])
        else:
            QMessageBox.critical(self, "Error", "Keyboard configuration file not found.")

    def open_joystick_config(self):
        """Open joystick configuration"""
        self.close_current_process()
        joystick_config_path = os.path.join(self.config_folder, "joystick_config.py")
        
        if os.path.exists(joystick_config_path):
            self.current_process = subprocess.Popen([sys.executable, joystick_config_path])
        else:
            QMessageBox.critical(self, "Error", "Joystick configuration file not found.")

    def close_current_process(self):
        """Safely terminate any running configuration processes"""
        if self.current_process:
            try:
                parent = psutil.Process(self.current_process.pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            finally:
                self.current_process = None

    def toggle_debug(self):
        """Toggle debug mode"""
        self.debug_active = not self.debug_active
        self.menu_drawer.debug_btn.setStyleSheet(
            "background-color: #5c5c5c;" if self.debug_active else ""
        )
        print(f"Debugging {'enabled' if self.debug_active else 'disabled'}")

    def keyPressEvent(self, event):
        """Handle key press events for debugging"""
        if self.debug_active:
            print(f"Key pressed: {event.text()}")

    def keyReleaseEvent(self, event):
        """Handle key release events for debugging"""
        if self.debug_active:
            print(f"Key released: {event.text()}")

    def closeEvent(self, event):
        """Clean up resources when closing"""
        if hasattr(self, 'video_thread'):
            self.video_thread.stop()
            self.video_thread.wait()
        
        # Close pygame
        pygame.quit()
        
        event.accept()

def main():
    app = QApplication(sys.argv)
    console = GameConsole()
    console.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
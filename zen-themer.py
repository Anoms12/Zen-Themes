import os
import sys
import configparser
import requests
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QListWidget,
    QLabel, QWidget, QDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl

# GitHub repository details
OWNER = "Anoms12"
REPO = "Zen-Themes"
BRANCH = "main"  # Default branch of your repo
BASE_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"
ZEN_INSTALLATION_URL = "https://zen-browser.app/download/"
CHROME_SETUP_URL = "https://docs.zen-browser.app/guides/live-editing"

class GitHubNavigator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zen Themes Manager")
        self.resize(800, 600)

        self.base_path = self.get_zen_path()
        if not self.base_path:
            self.show_error(f"Zen is not installed. Please install it from: {ZEN_INSTALLATION_URL}")
            sys.exit()

        self.profiles = self.get_profiles()
        if not self.profiles:
            self.show_error("No profiles found in Zen installation.")
            sys.exit()

        self.current_profile = None
        self.current_folder_path = ""  # Track the current folder path
        self.init_ui()

    def get_zen_path(self):
        """Check for Zen installation in OS-specific locations."""
        if sys.platform.startswith("win"):
            path = Path(os.getenv("APPDATA", "")) / "zen"
        elif sys.platform == "darwin":
            path = Path.home() / "Library" / "Application Support" / "zen"
        else:
            path = Path.home() / ".zen"

        return path if path.exists() else None

    def get_profiles(self):
        """Retrieve profiles from profiles.ini."""
        profiles_ini = self.base_path / "Profiles" / "profiles.ini"
        if not profiles_ini.exists():
            return None

        config = configparser.ConfigParser()
        config.read(profiles_ini)

        profiles = {}
        for section in config.sections():
            if section.startswith("Profile") and "Name" in config[section]:
                profiles[config[section]["Name"]] = config[section].get("Path", "")
        return profiles

    def init_ui(self):
        """Initialize the UI to select a profile."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

        label = QLabel("Select a profile to modify:")
        self.layout.addWidget(label)

        self.profile_listbox = QListWidget()
        self.profile_listbox.addItems(self.profiles.keys())
        self.profile_listbox.itemDoubleClicked.connect(self.select_profile)
        self.layout.addWidget(self.profile_listbox)

        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.close)
        self.layout.addWidget(exit_button)

    def select_profile(self):
        """Handle profile selection."""
        selected_item = self.profile_listbox.currentItem()
        if not selected_item:
            return
        self.current_profile = selected_item.text()

        profile_relative_path = self.profiles[self.current_profile]
        profile_path = self.base_path / profile_relative_path / "chrome"
        self.check_for_userChrome(profile_path)

    def check_for_userChrome(self, profile_path):
        """Check if userChrome.css exists in the profile path."""
        if not profile_path.exists():
            self.show_error(f"The 'chrome' folder is missing for profile '{self.current_profile}'.")
            return

        user_chrome_path = profile_path / "userChrome.css"
        if not user_chrome_path.exists():
            self.show_error(f"Please follow the setup instructions here: {CHROME_SETUP_URL}")
            return

        self.show_theme_options(user_chrome_path)

    def show_theme_options(self, user_chrome_path):
        """Display options to install or toggle Zen themes."""
        self.current_folder_path = ""  # Reset to root folder for GitHub

        # Clear previous layout and prepare new screen
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Add "Back" button to navigate back to profile selection
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.go_back_to_profile_selection)
        self.layout.addWidget(back_button)

        # Add label for theme import
        path_label = QLabel(f"Profile: {self.current_profile}")
        self.layout.addWidget(path_label)

        # Show GitHub folder contents
        self.display_folder_contents(user_chrome_path, self.current_folder_path)

    def display_folder_contents(self, user_chrome_path, folder_path):
        """Fetch and display the contents of the given folder."""
        files = self.fetch_github_files(folder_path)
        if files is None:
            self.show_error("Failed to fetch folder contents.")
            return

        # Clear the layout and display the folder contents
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Display the folder path
        path_label = QLabel(f"Current Folder: {folder_path if folder_path else '/'}")
        self.layout.addWidget(path_label)

        self.folder_listbox = QListWidget()
        for file in files:
            item_label = f"[Folder] {file['name']}" if file['type'] == "dir" else file['name']
            self.folder_listbox.addItem(item_label)
        self.folder_listbox.itemDoubleClicked.connect(lambda: self.handle_file_selection(user_chrome_path, files))
        self.layout.addWidget(self.folder_listbox)

        # Add import button to process current folder and subfolders
        import_button = QPushButton("Import Current Folder and Subfolders")
        import_button.clicked.connect(lambda: self.import_folder_and_subfolders(user_chrome_path, folder_path))
        self.layout.addWidget(import_button)

        # Back button for navigation within folders
        if folder_path:
            folder_back_button = QPushButton("Back to Parent Folder")
            folder_back_button.clicked.connect(lambda: self.navigate_back(user_chrome_path))
            self.layout.addWidget(folder_back_button)

    def fetch_github_files(self, path=""):
        """Fetch the list of files and folders from GitHub."""
        url = f"{BASE_URL}/{path}?ref={BRANCH}" if path else f"{BASE_URL}?ref={BRANCH}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None

    def handle_file_selection(self, user_chrome_path, files):
        """Handle user selection of a file or folder."""
        selected_item = self.folder_listbox.currentItem()
        if not selected_item:
            return

        selected_text = selected_item.text()
        is_folder = selected_text.startswith("[Folder]")
        selected_name = selected_text.split(" ", 1)[1] if is_folder else selected_text

        selected_file = next((f for f in files if f["name"] == selected_name), None)
        if not selected_file:
            return

        if selected_file["type"] == "dir":
            # Navigate into the folder
            self.current_folder_path = f"{self.current_folder_path}/{selected_name}" if self.current_folder_path else selected_name
            self.display_folder_contents(user_chrome_path, self.current_folder_path)
        elif selected_file["name"].endswith(".css"):
            # Add the selected theme
            self.add_theme_to_userChrome(user_chrome_path, selected_file)
        else:
            # Open a web link for non-CSS files
            QDesktopServices.openUrl(QUrl(selected_file["html_url"]))

    def navigate_back(self, user_chrome_path):
        """Navigate back to the parent folder."""
        if "/" in self.current_folder_path:
            self.current_folder_path = "/".join(self.current_folder_path.split("/")[:-1])
        else:
            self.current_folder_path = ""
        self.display_folder_contents(user_chrome_path, self.current_folder_path)

    def go_back_to_profile_selection(self):
        """Navigate back to the profile selection screen."""
        self.current_profile = None
        self.init_ui()

    def add_theme_to_userChrome(self, user_chrome_path, selected_file):
        """Add the selected theme to the userChrome.css file."""
        theme_content = requests.get(selected_file["download_url"]).text

        # Create zen-themer folder if it doesn't exist
        zen_themer_folder = user_chrome_path.parent / "zen-themer"
        zen_themer_folder.mkdir(parents=True, exist_ok=True)

        # Download the CSS file to the zen-themer folder
        local_css_path = zen_themer_folder / selected_file["name"]
        with open(local_css_path, "w") as f:
            f.write(theme_content)

        # Add @import statement to userChrome.css
        with open(user_chrome_path, "a") as f:
            f.write(f'@import "zen-themer/{selected_file["name"]}";\n')

        self.show_success(f"Added theme '{selected_file['name']}' to {user_chrome_path}")

    def import_folder_and_subfolders(self, user_chrome_path, folder_path):
        """Import the current folder and its subfolders into zen-themer."""
        files = self.fetch_github_files(folder_path)
        if not files:
            self.show_error("No files found in the folder to import.")
            return

        # Create zen-themer folder if it doesn't exist
        zen_themer_folder = user_chrome_path.parent / "zen-themer"
        zen_themer_folder.mkdir(parents=True, exist_ok=True)

        # Import all CSS files in the current folder and subfolders
        for file in files:
            if file['type'] == 'dir':
                # Recursively import subfolders
                self.import_folder_and_subfolders(user_chrome_path, f"{folder_path}/{file['name']}")
            elif file['name'].endswith('.css'):
                # Download and save the CSS file to zen-themer
                self.add_theme_to_userChrome(user_chrome_path, file)

        self.show_success(f"Imported folder and subfolders into {zen_themer_folder}")

    def show_error(self, message):
        """Display an error message."""
        QMessageBox.critical(self, "Error", message)

    def show_success(self, message):
        """Display a success message."""
        QMessageBox.information(self, "Success", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GitHubNavigator()
    window.show()
    sys.exit(app.exec())

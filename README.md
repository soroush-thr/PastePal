# PastePal - Advanced Clipboard Manager

A powerful, feature-rich clipboard manager for Windows built with Python and PyQt6. PastePal enhances your productivity by providing intelligent clipboard management with a modern, compact interface that opens near the middle-right of your screen.

## Features

### Core Functionality
- **System Tray Operation**: Runs silently in the background with system tray integration
- **Global Hotkeys**: Quick access with customizable hotkeys (default: Alt+V)
- **Clipboard Monitoring**: Automatically captures all clipboard content
- **Multi-Content Support**: Handles text, rich text, images, and files/folders

### User Interface
- **Compact, Responsive Design**: Optimized 450x350 window with efficient space usage
- **Smart Positioning**: Opens near middle-right of screen for optimal accessibility
- **Clean, Modern UI**: Beautiful interface with light and dark themes
- **Real-time Search**: Debounced search with instant filtering
- **Smart Previews**: See content previews with appropriate icons and better separation
- **Visual Click Feedback**: Immediate visual response when clicking items
- **Keyboard Navigation**: Full keyboard support for power users

### Advanced Features
- **Pinned Items**: Pin important items for quick access
- **Text Transformations**: Convert text to uppercase, lowercase, title case, or trim whitespace
- **Merge Text**: Combine multiple text items into one
- **Plain Text Pasting**: Strip formatting when pasting (Ctrl+Shift+Enter)
- **Settings Panel**: Comprehensive configuration options

### Data Management
- **SQLite Database**: Reliable local storage for clipboard history
- **Performance Optimized**: Efficient database queries with 50-item limit for fast loading
- **Auto-cleanup**: Automatic removal of old items to manage storage
- **Export/Import**: Easy data management and backup
- **Memory Efficient**: Optimized widget management and cleanup

## Installation

### Prerequisites
- Windows 10/11
- Python 3.10 or higher

### From Source
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/pastepal.git
   cd pastepal
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python -m pastepal.main
   ```

### Building Executable
1. Run the build script:
   ```bash
   python build.py
   ```

2. Find the executable in `dist/PastePal/PastePal.exe`

## Usage

### Getting Started
1. Launch PastePal - it will start minimized in the system tray
2. Copy some text, images, or files to your clipboard
3. Press `Alt+V` (or your configured hotkey) to open the main window
4. Browse your clipboard history and select items to paste

### Keyboard Shortcuts
- `Alt+V`: Show/hide main window
- `Enter`: Paste selected item
- `Ctrl+Shift+Enter`: Paste as plain text
- `Escape`: Hide main window
- `Ctrl+A`: Select all items

### Right-Click Menu
- **Pin/Unpin**: Pin important items to the top
- **Copy to Clipboard**: Copy item back to clipboard
- **Transform Text**: Convert text case or trim whitespace
- **Delete**: Remove item from history

### Settings
Access settings through the system tray menu or the settings button in the main window:

- **General**: Startup options, history limits, monitoring settings
- **Appearance**: Theme selection, window size, display options
- **Hotkeys**: Customize global hotkeys
- **Advanced**: Database management, performance settings

## Configuration

### Hotkeys
Configure global hotkeys in the settings panel:
- Show window: Default `Alt+V`
- Paste as plain text: Default `Ctrl+Shift+Enter`
- Quick paste: Default `Ctrl+Alt+V`

### Themes
Choose between light and dark themes, with more themes coming soon.

### History Management
- Set maximum history items (default: 1000)
- Enable/disable auto-cleanup
- Clear history on exit option

## Development

### Project Structure
```
pastepal/
├── main.py                 # Application entry point
├── database.py            # Database models and operations
├── clipboard_monitor.py   # Clipboard monitoring service
├── hotkeys.py             # Global hotkey management
├── ui/
│   ├── main_window.py     # Main application window
│   ├── settings_dialog.py # Settings dialog
│   ├── system_tray.py     # System tray functionality
│   └── themes.py          # Theme management
├── requirements.txt       # Python dependencies
├── setup.py              # Package setup
├── pastepal.spec         # PyInstaller configuration
├── build.py              # Build script
└── version_info.txt      # Version information
```

### Building
The project includes a comprehensive build system:

1. **Dependencies**: Install all required packages
2. **Executable**: Create standalone executable with PyInstaller
3. **Portable**: Generate portable version
4. **Installer**: Create Windows installer (requires Inno Setup)

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Technical Details

### Architecture
- **GUI Framework**: PyQt6 for modern, native Windows UI
- **Database**: SQLite for reliable local storage
- **Hotkeys**: Global hotkey support using the `keyboard` library
- **Clipboard**: Windows clipboard API integration
- **Packaging**: PyInstaller for executable creation

### Performance
- Efficient clipboard monitoring with configurable intervals
- Smart database cleanup to manage storage
- Minimal memory footprint with optimized widget management
- Fast search and filtering with debounced input
- Compact UI design for improved responsiveness
- Reduced database query limits for faster loading

### Security
- All data stored locally
- No network communication
- No data collection or telemetry
- Open source and auditable

## Troubleshooting

### Common Issues
1. **Hotkeys not working**: Run as administrator or check antivirus settings
2. **Clipboard not monitored**: Check if monitoring is enabled in settings
3. **High CPU usage**: Increase monitoring interval in settings
4. **Database errors**: Delete `pastepal.db` to reset

### Support
- Check the [Issues](https://github.com/yourusername/pastepal/issues) page
- Create a new issue with detailed information
- Include system information and error logs

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [PyQt6](https://www.riverbankcomputing.com/software/pyqt/)
- Uses [Pillow](https://python-pillow.org/) for image processing
- Global hotkeys powered by [keyboard](https://github.com/boppreh/keyboard)
- Packaged with [PyInstaller](https://www.pyinstaller.org/)

## Changelog

### Version 1.1.0 - UI Improvements
- **Compact Design**: Reduced window size to 450x350 for better space efficiency
- **Smart Positioning**: Window now opens near middle-right of screen instead of cursor center
- **Enhanced Responsiveness**: Fixed click issues and added visual feedback animations
- **Better Item Separation**: Improved spacing and visual separation between clipboard items
- **Performance Optimizations**: Debounced search, reduced database queries, optimized memory usage
- **Visual Feedback**: Added click flash animations and improved hover states
- **UI Polish**: Better borders, rounded corners, and improved color schemes

### Version 1.0.0 - Initial Release
- Core clipboard management functionality
- System tray integration
- Global hotkey support
- Light and dark themes
- Text transformation tools
- Pinned items support
- Comprehensive settings panel
- Windows installer and portable versions

## Documentation

Additional documentation is available in the `markdowns/` directory:
- `github-repository-description.md` - GitHub repository description and topics
- `linkedin-project-description.md` - LinkedIn project description for portfolio
- `project-creation-git-commands.md` - Complete Git workflow and commit history
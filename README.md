# GESTURA - Hand Gesture Recognition System

GESTURA is a comprehensive hand gesture recognition system that enables users to control their computer using hand gestures. The project consists of three main components: a desktop application, a sign prediction module, and an ISL (Indian Sign Language) overlay system.

## Project Structure

```
GESTURA/
├── desktopIntegration/     # Desktop application for gesture recognition
├── signpred/              # Sign prediction module
└── isloverlay/           # ISL overlay system
```

## Features

- Real-time hand gesture recognition using MediaPipe
- Custom gesture recording and playback
- Desktop control through hand gestures
- Indian Sign Language support
- Cross-platform compatibility
- Modern UI with CustomTkinter

## Components

### 1. Desktop Integration
- Real-time hand tracking and gesture recognition
- Custom gesture recording interface
- Gesture-to-action mapping
- System control through gestures

### 2. Sign Prediction
- Advanced sign language recognition
- Real-time prediction
- Cross-platform support (Windows, macOS, Linux, Android, iOS)

### 3. ISL Overlay
- Indian Sign Language support
- Real-time overlay system
- Educational features

## Requirements

### Desktop Integration
- Python 3.8+
- OpenCV
- MediaPipe
- CustomTkinter
- PyAutoGUI
- Other dependencies listed in `desktopIntegration/requirements.txt`

### Sign Prediction & ISL Overlay
- Flutter/Dart
- Platform-specific dependencies

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/GESTURA.git
cd GESTURA
```

2. Install desktop integration dependencies:
```bash
cd desktopIntegration
pip install -r requirements.txt
```

3. For sign prediction and ISL overlay:
```bash
cd signpred  # or isloverlay
flutter pub get
```

## Usage

### Desktop Integration
1. Run the main application:
```bash
cd desktopIntegration
python main.py
```

2. Record custom gestures:
```bash
python record_gestures2.py
```

### Sign Prediction
```bash
cd signpred
flutter run
```

### ISL Overlay
```bash
cd isloverlay
flutter run
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- MediaPipe for hand tracking capabilities
- CustomTkinter for the modern UI components
- Flutter team for cross-platform support 
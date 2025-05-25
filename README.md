# PyQt Overlay Application

## Description

This is a desktop application that displays one or more overlay windows. The text content and appearance (opacity, background color, font) of these overlay windows can be customized through a central input/control window.

Key features include:
- Multiple independent overlay windows.
- Dynamic text updates for all overlays.
- Customizable appearance:
    - Window opacity/transparency.
    - Background color.
    - Font for the displayed text.
- Frameless, draggable, and resizable overlay windows.
- Smooth text fade-in/out animations on text change.
- Smooth mouse-wheel driven scrolling for text overflow.
- Persistence of the main text content for the first overlay window.

## Dependencies

The primary dependency for this application is PyQt6.

- `PyQt6`

## Installation and Running

1.  **Clone the repository or download the source code.**

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    Open a terminal or command prompt in the project root directory (where `requirements.txt` is located) and run:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    Once dependencies are installed, run the main script:
    ```bash
    python main.py
    ```
    This will open the main Input & Control window and an initial overlay window.

## Packaging with PyInstaller

To package the application into a single executable file (e.g., for Windows), you can use PyInstaller.

1.  **Install PyInstaller:**
    If you don't have PyInstaller installed, install it via pip:
    ```bash
    pip install pyinstaller
    ```

2.  **Build the executable:**
    Open a terminal or command prompt in the project root directory and run the following command:
    ```bash
    pyinstaller --onefile --windowed --name PyQtOverlayApp main.py
    ```
    *   `--onefile`: Bundles everything into a single executable.
    *   `--windowed`: Prevents a command-line console window from appearing when the application runs (since it's a GUI application).
    *   `--name PyQtOverlayApp`: Specifies the name of the output executable.
    *   `main.py`: The entry point script for the application.

    **Optional: Adding an Icon (Windows)**
    If you have an icon file (e.g., `icon.ico`), you can include it:
    ```bash
    pyinstaller --onefile --windowed --name PyQtOverlayApp --icon="path/to/your/icon.ico" main.py
    ```

3.  **Find the executable:**
    After PyInstaller finishes, the executable will be located in a `dist` subfolder within your project directory (e.g., `dist/PyQtOverlayApp.exe`).

    **Note on `saved_text.txt`**:
    The application saves text to `saved_text.txt` in the same directory where the executable is run. If packaged with `--onefile`, this means `saved_text.txt` will appear next to your `.exe` file after the first run where text is saved.

## Feature Checklist for Testing

This checklist can be used to manually test the application's features:

**I. Core Application & Window Management**
*   [ ] **Initial Startup**:
    *   Does the `InputWindow` (control panel) open correctly?
    *   Does an initial `OverlayWindow` open correctly?
*   [ ] **Input Window Functionality**:
    *   Text input field is present.
    *   "Submit Text" button is present.
    *   "New Overlay Window" button is present.
    *   Opacity slider is present and defaults to 100%.
    *   "Change Background Color" button is present.
    *   "Change Font" button is present.
*   [ ] **New Overlay Window Creation**:
    *   Clicking "New Overlay Window" creates a new, independent `OverlayWindow`.
    *   New windows appear with default text (e.g., "New Overlay X").
    *   New windows appear with current global customization settings (opacity, color, font).
    *   New windows are slightly offset from the previous one.
*   [ ] **Overlay Window Closing**:
    *   Clicking the 'X' button on an `OverlayWindow` closes only that specific window.
    *   Other `OverlayWindow`s and the `InputWindow` remain open.
*   [ ] **Application Exit**:
    *   Closing the `InputWindow` closes all open `OverlayWindow`s and quits the application.

**II. Overlay Window Features**
*   [ ] **Appearance & Basic Structure**:
    *   Is the `OverlayWindow` frameless?
    *   Does it have rounded corners (15px)?
    *   Is the 'X' button visible in the top-left and functional?
*   [ ] **Text Display & Updates**:
    *   Text submitted from `InputWindow` updates the text in all open `OverlayWindow`(s).
    *   If text is empty, a default placeholder is shown in overlays (e.g., "Overlay X").
    *   Text fade-in/out animation occurs smoothly when text changes.
*   [ ] **Window Manipulation**:
    *   Can each `OverlayWindow` be dragged independently using the mouse?
    *   Can each `OverlayWindow` be resized independently by dragging its borders/corners?
    *   Do resize cursors appear correctly when hovering over borders/corners?
    *   Is there a minimum window size enforced?
*   [ ] **Text Scrolling**:
    *   If text content exceeds the `OverlayWindow`'s dimensions, is it scrollable via the mouse wheel?
    *   Is the scrolling smooth (animated)?
    *   Are scrollbars hidden?
    *   Does scrolling reset to the top when text content is updated?

**III. Customization**
*   [ ] **Opacity/Transparency**:
    *   Does the opacity slider in `InputWindow` control the transparency of all current and future `OverlayWindow`s?
    *   Does the opacity range from slightly transparent (20%) to fully opaque (100%)?
*   [ ] **Background Color**:
    *   Does the "Change Background Color" button open a color dialog?
    *   Does selecting a color apply it to the background of all current and future `OverlayWindow`s?
    *   Are rounded corners preserved after color change?
*   [ ] **Font**:
    *   Does the "Change Font" button open a font dialog?
    *   Does selecting a font (family, size, style) apply it to the text in all current and future `OverlayWindow`s?

**IV. Persistence**
*   [ ] **Text Persistence (First Window)**:
    *   Enter text into an `OverlayWindow` (if multiple are open, ensure it's reflected in the first one created, which is usually the one loaded from save or the first one if no save existed).
    *   Close the application (via `InputWindow`).
    *   Re-run the application.
    *   Does the *first* `OverlayWindow` load with the previously saved text?
    *   If `saved_text.txt` is deleted, does the first window start with default text?
*   [ ] **Customization Persistence (Not Implemented)**:
    *   Verify that opacity, background color, and font settings are *not* saved/loaded (as per current scope). They should reset to default on each application start.

**V. General Stability**
*   [ ] **No Crashes**: Application runs without unexpected crashes during normal use of features.
*   [ ] **Responsiveness**: UI remains responsive during operations.
*   [ ] **Resource Usage**: (Optional) Check if resource usage is reasonable.
```

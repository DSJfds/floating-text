import sys
import os 
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, 
                             QVBoxLayout, QLineEdit, QHBoxLayout, 
                             QGraphicsOpacityEffect, QScrollArea, QScrollBar,
                             QSizePolicy, QSlider, QColorDialog, QFontDialog) # Added controls
from PyQt6.QtGui import QColor, QFont # Added QColor, QFont
from PyQt6.QtCore import (Qt, QPoint, QPointF, QRect, QSize, pyqtSignal, QPropertyAnimation, 
                          QEasingCurve, pyqtSlot, QEvent, QObject) 

SAVE_FILE_PATH = "saved_text.txt" # For main text content
# Persistence for new settings (opacity, color, font) is deferred for this step.

overlay_windows = [] 
next_window_id = 1

DEFAULT_OPACITY = 1.0
DEFAULT_BG_COLOR = QColor("white")
DEFAULT_FONT = QFont("Arial", 18) # Default font with a size

class InputWindow(QWidget):
    text_submitted = pyqtSignal(str)
    request_new_overlay = pyqtSignal()
    is_closing = pyqtSignal()

    # Signals for customization changes
    opacity_changed = pyqtSignal(int) # int value from slider (20-100)
    background_color_changed = pyqtSignal(QColor)
    font_changed = pyqtSignal(QFont)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Text Input & Customization")
        self.initUI()
        self.resize(400, 250) 

    def initUI(self):
        main_layout = QVBoxLayout(self)

        # Text Input
        text_input_layout = QHBoxLayout()
        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText("Enter text for overlays")
        self.text_input.returnPressed.connect(self.submit_text)
        text_input_layout.addWidget(self.text_input)
        self.submit_button = QPushButton("Submit Text")
        self.submit_button.clicked.connect(self.submit_text)
        text_input_layout.addWidget(self.submit_button)
        main_layout.addLayout(text_input_layout)

        # New Overlay Button
        self.new_overlay_button = QPushButton("New Overlay Window")
        self.new_overlay_button.clicked.connect(self.request_new_overlay.emit)
        main_layout.addWidget(self.new_overlay_button)

        # Opacity Slider
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setMinimum(20) # 20%
        self.opacity_slider.setMaximum(100) # 100%
        self.opacity_slider.setValue(int(DEFAULT_OPACITY * 100))
        self.opacity_slider.valueChanged.connect(self.opacity_changed.emit)
        opacity_layout.addWidget(self.opacity_slider)
        main_layout.addLayout(opacity_layout)

        # Color Button
        self.color_button = QPushButton("Change Background Color")
        self.color_button.clicked.connect(self.open_color_dialog)
        main_layout.addWidget(self.color_button)

        # Font Button
        self.font_button = QPushButton("Change Font")
        self.font_button.clicked.connect(self.open_font_dialog)
        main_layout.addWidget(self.font_button)
        
        self.setLayout(main_layout)

    def submit_text(self):
        text = self.text_input.text()
        self.text_submitted.emit(text)

    def open_color_dialog(self):
        color = QColorDialog.getColor(DEFAULT_BG_COLOR, self, "Select Background Color")
        if color.isValid():
            self.background_color_changed.emit(color)

    def open_font_dialog(self):
        font, ok = QFontDialog.getFont(DEFAULT_FONT, self, "Select Font")
        if ok:
            self.font_changed.emit(font)

    def closeEvent(self, event):
        self.is_closing.emit() 
        super().closeEvent(event)


class OverlayWindow(QWidget):
    closed_signal = pyqtSignal(QWidget) 

    def __init__(self, window_id="1", initial_text=None, is_first_window=False,
                 opacity=DEFAULT_OPACITY, bg_color=None, font=None): # Added customization params
        super().__init__()
        
        self.window_id = window_id
        self.is_first_window = is_first_window
        self._bg_color = bg_color or DEFAULT_BG_COLOR # Store current bg color
        self._font = font or DEFAULT_FONT # Store current font

        if initial_text is not None: self.current_text = initial_text
        elif self.is_first_window and os.path.exists(SAVE_FILE_PATH): self.load_text_on_init()
        else: self.current_text = f"New Overlay {self.window_id}"

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        # Initial stylesheet set here, will be updated by set_background_color
        self.setStyleSheet(f"OverlayWindow {{ background-color: {self._bg_color.name()}; border-radius: 15px; }}")
        self.set_opacity(opacity) # Apply initial opacity

        self.initUI() 
        self.set_font(self._font) # Apply initial font to label after UI is created
        
        self.opacity_effect_text = QGraphicsOpacityEffect(self.label) # For text fade
        self.label.setGraphicsEffect(self.opacity_effect_text)
        self.opacity_effect_text.setOpacity(1.0) 

        self.active_text_animation = None 
        self.active_scroll_animation = None 
        
        self.oldPos = None; self.resizing = False; self.resize_edge = None
        self.resize_margin = 10; self.resize_start_geometry = None; self.resize_start_pos = None

        self.setMouseTracking(True) 
        self.setMinimumSize(150, 80) 
        self.move(50 + (int(window_id)-1)*20, 50 + (int(window_id)-1)*20)
        self.resize(300, 150)

    def load_text_on_init(self):
        try:
            with open(SAVE_FILE_PATH, "r", encoding="utf-8") as f:
                text = f.read(); self.current_text = text if text else "Hello, Overlay!"
        except Exception as e: print(f"Error loading text: {e}"); self.current_text = "Hello, Overlay!"

    def initUI(self):
        self.main_layout = QVBoxLayout(self) 
        self.main_layout.setContentsMargins(10, 25, 10, 10) 
        self.label = QLabel(self.current_text, self) 
        self.label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft) 
        self.label.setWordWrap(True) 
        self.label.setStyleSheet("background-color: transparent; color: black;") # Font size/family from set_font
        self.label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.label.adjustSize()
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True); self.scroll_area.setWidget(self.label)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.main_layout.addWidget(self.scroll_area)
        self.close_button = QPushButton("X", self)
        self.close_button.setStyleSheet("""
            QPushButton { background-color: #FF605C; color: black; border: 1px solid #D04844;
                          border-radius: 7px; font-weight: bold; font-size: 10px;
                          min-width: 14px; min-height: 14px; max-width: 14px; max-height: 14px; }
            QPushButton:hover { background-color: #E04A46; } QPushButton:pressed { background-color: #C03430; }""")
        self.close_button.clicked.connect(self.handle_close_request)
        self.close_button.setFixedSize(14, 14)
        self.setLayout(self.main_layout)

    # --- Customization Methods ---
    def set_opacity(self, opacity_percentage): # opacity_percentage is 0-100
        self.setWindowOpacity(opacity_percentage / 100.0)

    def set_background_color(self, color: QColor):
        self._bg_color = color
        # Update stylesheet, preserving border-radius
        self.setStyleSheet(f"OverlayWindow {{ background-color: {color.name()}; border-radius: 15px; }}")

    def set_font(self, font: QFont):
        self._font = font
        self.label.setFont(font)
        # Adjust label stylesheet if font color should contrast with background, or handle globally
        # For now, label text color is fixed to black via its own stylesheet.

    def handle_close_request(self): self.closed_signal.emit(self)
    def get_resize_edge(self, pos: QPointF):
        rect = self.rect(); m = self.resize_margin
        if pos.x() < m and pos.y() < m: return Qt.Corner.TopLeftCorner
        if pos.x() > rect.right() - m and pos.y() < m: return Qt.Corner.TopRightCorner
        if pos.x() < m and pos.y() > rect.bottom() - m: return Qt.Corner.BottomLeftCorner
        if pos.x() > rect.right() - m and pos.y() > rect.bottom() - m: return Qt.Corner.BottomRightCorner
        if pos.x() < m: return Qt.Edge.LeftEdge
        if pos.x() > rect.right() - m: return Qt.Edge.RightEdge
        if pos.y() < m: return Qt.Edge.TopEdge
        if pos.y() > rect.bottom() - m: return Qt.Edge.BottomEdge
        return None
    def update_cursor_shape(self, pos: QPointF):
        if not self.resizing: 
            edge = self.get_resize_edge(pos)
            if edge == Qt.Corner.TopLeftCorner or edge == Qt.Corner.BottomRightCorner: self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif edge == Qt.Corner.TopRightCorner or edge == Qt.Corner.BottomLeftCorner: self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            elif edge == Qt.Edge.LeftEdge or edge == Qt.Edge.RightEdge: self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif edge == Qt.Edge.TopEdge or edge == Qt.Edge.BottomEdge: self.setCursor(Qt.CursorShape.SizeVerCursor)
            else: self.unsetCursor()
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.oldPos = None; self.resizing = False; current_pos_local = event.position()
            self.resize_edge = self.get_resize_edge(current_pos_local)
            if self.resize_edge: self.resizing = True; self.resize_start_geometry = self.geometry(); self.resize_start_pos = event.globalPosition(); event.accept(); return
            if self.close_button.geometry().contains(current_pos_local.toPoint()): super().mousePressEvent(event); return
            self.oldPos = event.globalPosition().toPoint(); event.accept(); return
        super().mousePressEvent(event)
    def mouseMoveEvent(self, event):
        self.update_cursor_shape(event.position())
        if self.resizing and event.buttons() == Qt.MouseButton.LeftButton:
            if not self.resize_start_pos: self.resizing = False; return 
            delta = event.globalPosition() - self.resize_start_pos; new_geometry = QRect(self.resize_start_geometry)
            if self.resize_edge == Qt.Edge.TopEdge: new_geometry.setTop(new_geometry.top() + int(delta.y()))
            elif self.resize_edge == Qt.Edge.BottomEdge: new_geometry.setBottom(new_geometry.bottom() + int(delta.y()))
            elif self.resize_edge == Qt.Edge.LeftEdge: new_geometry.setLeft(new_geometry.left() + int(delta.x()))
            elif self.resize_edge == Qt.Edge.RightEdge: new_geometry.setRight(new_geometry.right() + int(delta.x()))
            elif self.resize_edge == Qt.Corner.TopLeftCorner: new_geometry.setTop(new_geometry.top()+int(delta.y())); new_geometry.setLeft(new_geometry.left()+int(delta.x()))
            elif self.resize_edge == Qt.Corner.TopRightCorner: new_geometry.setTop(new_geometry.top()+int(delta.y())); new_geometry.setRight(new_geometry.right()+int(delta.x()))
            elif self.resize_edge == Qt.Corner.BottomLeftCorner: new_geometry.setBottom(new_geometry.bottom()+int(delta.y())); new_geometry.setLeft(new_geometry.left()+int(delta.x()))
            elif self.resize_edge == Qt.Corner.BottomRightCorner: new_geometry.setBottom(new_geometry.bottom()+int(delta.y())); new_geometry.setRight(new_geometry.right()+int(delta.x()))
            min_w, min_h = self.minimumWidth(), self.minimumHeight()
            if new_geometry.width() < min_w:
                if self.resize_edge==Qt.Edge.LeftEdge or self.resize_edge==Qt.Corner.TopLeftCorner or self.resize_edge==Qt.Corner.BottomLeftCorner: new_geometry.setLeft(new_geometry.right()-min_w)
                else: new_geometry.setWidth(min_w)
            if new_geometry.height() < min_h:
                if self.resize_edge==Qt.Edge.TopEdge or self.resize_edge==Qt.Corner.TopLeftCorner or self.resize_edge==Qt.Corner.TopRightCorner: new_geometry.setTop(new_geometry.bottom()-min_h)
                else: new_geometry.setHeight(min_h)
            self.setGeometry(new_geometry); event.accept(); return
        elif self.oldPos and event.buttons() == Qt.MouseButton.LeftButton:
            delta_drag = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta_drag.x(), self.y() + delta_drag.y())
            self.oldPos = event.globalPosition().toPoint(); event.accept(); return
        super().mouseMoveEvent(event)
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.resizing: self.resizing=False; self.resize_edge=None; self.resize_start_pos=None; self.resize_start_geometry=None; self.unsetCursor(); event.accept(); return 
            elif self.oldPos: self.oldPos=None; event.accept(); return 
        super().mouseReleaseEvent(event)
    def resizeEvent(self, event): super().resizeEvent(event); self.close_button.move(5, 5) 
    def wheelEvent(self, event):
        vsb = self.scroll_area.verticalScrollBar(); current_value = vsb.value()
        scroll_amount = event.angleDelta().y()/120 * vsb.singleStep()*3; new_target_value = current_value - int(scroll_amount)
        if self.active_scroll_animation and self.active_scroll_animation.state()==QPropertyAnimation.State.Running:
            current_value = self.active_scroll_animation.currentValue(); self.active_scroll_animation.stop()
        self.active_scroll_animation = QPropertyAnimation(vsb, b"value", self); self.active_scroll_animation.setDuration(150)
        self.active_scroll_animation.setStartValue(current_value); self.active_scroll_animation.setEndValue(new_target_value)
        self.active_scroll_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.active_scroll_animation.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped); event.accept()
    @pyqtSlot(str)
    def update_text(self, new_text):
        effective_new_text = new_text if new_text else f"Overlay {self.window_id}"
        self.scroll_area.verticalScrollBar().setValue(0)
        if self.label.text() == effective_new_text and self.opacity_effect_text.opacity()==1.0: return 
        if self.active_text_animation and self.active_text_animation.state()==QPropertyAnimation.State.Running: self.active_text_animation.stop() 
        def start_fade_in():
            self.label.setText(effective_new_text); self.current_text = effective_new_text 
            fade_in_anim = QPropertyAnimation(self.opacity_effect_text, b"opacity")
            fade_in_anim.setDuration(300); fade_in_anim.setStartValue(0.0); fade_in_anim.setEndValue(1.0)
            fade_in_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.active_text_animation = fade_in_anim
            fade_in_anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        if self.opacity_effect_text.opacity() > 0:
            fade_out_anim = QPropertyAnimation(self.opacity_effect_text, b"opacity")
            fade_out_anim.setDuration(300); fade_out_anim.setStartValue(self.opacity_effect_text.opacity()); fade_out_anim.setEndValue(0.0)
            fade_out_anim.setEasingCurve(QEasingCurve.Type.InOutQuad); fade_out_anim.finished.connect(start_fade_in)
            self.active_text_animation = fade_out_anim; fade_out_anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        else: start_fade_in()

class MainApplication(QObject):
    def __init__(self, app_instance): # Renamed app to app_instance to avoid conflict
        super().__init__()
        self.app_instance = app_instance # Store QApplication instance
        self.input_window = InputWindow()
        
        # Global customization settings
        self.current_opacity = int(DEFAULT_OPACITY * 100) # Store as 20-100
        self.current_bg_color = DEFAULT_BG_COLOR
        self.current_font = DEFAULT_FONT

        self.input_window.text_submitted.connect(self.update_all_overlay_text)
        self.input_window.request_new_overlay.connect(self.create_new_overlay_window_handler)
        self.input_window.is_closing.connect(self.handle_input_window_closing)
        
        # Connect customization signals
        self.input_window.opacity_changed.connect(self.set_global_opacity)
        self.input_window.background_color_changed.connect(self.set_global_background_color)
        self.input_window.font_changed.connect(self.set_global_font)

        self.create_initial_overlay_window()
        self.input_window.show()
        self.app_instance.aboutToQuit.connect(self.save_first_window_text_on_exit)

    def create_new_overlay_window(self, window_id_str, initial_text=None, is_first=False):
        global overlay_windows # Keep using global list for now
        overlay = OverlayWindow(window_id=window_id_str, initial_text=initial_text, is_first_window=is_first,
                                opacity=self.current_opacity / 100.0, # Pass current global settings
                                bg_color=self.current_bg_color,
                                font=self.current_font)
        overlay.closed_signal.connect(self.remove_overlay_window)
        overlay_windows.append(overlay)
        overlay.show()
        return overlay
        
    def create_new_overlay_window_handler(self): # Slot for request_new_overlay signal
        global next_window_id
        window_id_str = str(next_window_id)
        next_window_id += 1
        self.create_new_overlay_window(window_id_str=window_id_str, is_first=False)


    def create_initial_overlay_window(self):
        global next_window_id
        self.create_new_overlay_window(window_id_str=str(next_window_id), is_first=True)
        next_window_id +=1


    def update_all_overlay_text(self, text):
        global overlay_windows
        if not overlay_windows: 
            self.create_new_overlay_window(window_id_str=str(next_window_id), initial_text=text if text else "Hello, Overlay!", is_first=True)
            next_window_id +=1
        else:
            for window in overlay_windows: window.update_text(text)

    def remove_overlay_window(self, window_instance):
        global overlay_windows
        if window_instance in overlay_windows: overlay_windows.remove(window_instance)
        window_instance.close() 

    def handle_input_window_closing(self):
        global overlay_windows
        for window in list(overlay_windows): window.close()
        overlay_windows.clear()
        self.app_instance.quit()

    def save_first_window_text_on_exit(self):
        global overlay_windows
        if overlay_windows:
            try:
                with open(SAVE_FILE_PATH, "w", encoding="utf-8") as f: f.write(overlay_windows[0].current_text)
            except Exception as e: print(f"Error saving text: {e}")

    # --- Global Customization Setters ---
    @pyqtSlot(int)
    def set_global_opacity(self, opacity_val): # Opacity 20-100
        self.current_opacity = opacity_val
        for window in overlay_windows: window.set_opacity(opacity_val)

    @pyqtSlot(QColor)
    def set_global_background_color(self, color: QColor):
        self.current_bg_color = color
        for window in overlay_windows: window.set_background_color(color)

    @pyqtSlot(QFont)
    def set_global_font(self, font: QFont):
        self.current_font = font
        for window in overlay_windows: window.set_font(font)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app_logic = MainApplication(app)
    sys.exit(app.exec())

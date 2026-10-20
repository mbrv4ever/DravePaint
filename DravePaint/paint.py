#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DravePaint - a simple, MS Paint-style image editor with layers  (a Dravenlock product)

Lightweight PyQt6 app: a canvas with layers, the familiar simple tools (pencil,
brush, eraser, fill, eyedropper, line, rectangle, ellipse, text, move), a colour
picker, undo/redo, zoom, its own .dravepaint project format and import/export of
all common image types (PNG, JPG, BMP, GIF, WEBP, TIFF, ...). Dutch base language
with automatic OS-language detection. Large, high-contrast UI for readability.
"""

import sys
import os
import json
import base64
import locale

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QFileDialog, QColorDialog, QSlider, QListWidget,
    QListWidgetItem, QAbstractItemView, QDialog, QSpinBox, QLineEdit, QComboBox,
    QMessageBox, QInputDialog, QScrollArea, QFrame, QSizePolicy, QStatusBar,
    QFontComboBox, QCheckBox,
)
from PyQt6.QtGui import (
    QImage, QPixmap, QPainter, QColor, QPen, QBrush, QIcon, QAction, QFont,
    QPainterPath, QPolygon, QTransform, QRadialGradient,
)
from PyQt6.QtCore import Qt, QPoint, QRect, QSize, QLocale, QTranslator, QLibraryInfo

try:
    from PIL import Image, ImageDraw
    HAVE_PIL = True
except Exception:
    HAVE_PIL = False

# ----------------------------------------------------------------------------- meta
APP_NAME = "DravePaint"
APP_VERSION = "0.1.11"
AUTHOR_NAME = "Dravenlock"
WEBSITE_URL = "https://dravenlock.nl/"
DONATE_URL = "https://paypal.me/roger076"

# ----------------------------------------------------------------------------- palette
BG = "#0e0e11"
PANEL = "#16161b"
PANEL2 = "#1c1c22"
LINE = "#2c2c34"
TEXT = "#d4d4d4"
MUTED = "#8a8a93"
ACCENT = "#6fa3d6"
GOOD = "#7fb069"
WARN = "#d68a6f"

# ----------------------------------------------------------------------------- language
def _detect_lang():
    try:
        loc = QLocale.system().name().lower()      # bv. nl_nl / en_us
        if loc.startswith("nl"):
            return "nl"
        if loc.startswith("en"):
            return "en"
    except Exception:
        pass
    try:
        code = (locale.getdefaultlocale()[0] or "").lower()
        if code.startswith("nl"):
            return "nl"
        if code.startswith("en"):
            return "en"
    except Exception:
        pass
    return "nl"     # Dravenlock-basistaal is Nederlands


def _config_dir():
    base = os.environ.get("APPDATA") or os.path.expanduser("~")
    d = os.path.join(base, "DravePaint")
    try:
        os.makedirs(d, exist_ok=True)
    except Exception:
        pass
    return d


def load_lang():
    try:
        with open(os.path.join(_config_dir(), "config.json"), encoding="utf-8") as f:
            return json.load(f).get("lang")
    except Exception:
        return None


def save_lang(code):
    try:
        with open(os.path.join(_config_dir(), "config.json"), "w", encoding="utf-8") as f:
            json.dump({"lang": code}, f)
    except Exception:
        pass


LANG = "nl"

_qt_translators = []


def install_qt_translators(lang):
    """Laadt Qt's eigen vertalingen zodat standaardknoppen (Opslaan/Annuleren/Ja/Nee)
    in de juiste taal staan."""
    app = QApplication.instance()
    if app is None:
        return
    for tr in _qt_translators:
        app.removeTranslator(tr)
    _qt_translators.clear()
    QLocale.setDefault(QLocale(QLocale.Language.Dutch if lang == "nl"
                               else QLocale.Language.English))
    path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
    for base in ("qtbase", "qt"):
        tr = QTranslator()
        if tr.load(base + "_" + lang, path):
            app.installTranslator(tr)
            _qt_translators.append(tr)

# Dutch is the source language; values are English translations.
TRANSLATIONS = {
    "en": {
        "Bestand": "File", "Nieuw": "New", "Openen...": "Open...",
        "Openen als laag...": "Open as layer...",
        "Opslaan project...": "Save project...", "Exporteren...": "Export...",
        "Afsluiten": "Quit", "Bewerken": "Edit", "Ongedaan maken": "Undo",
        "Opnieuw": "Redo", "Beeld": "View", "Inzoomen": "Zoom in",
        "Uitzoomen": "Zoom out", "Werkelijke grootte": "Actual size",
        "Passend maken": "Fit to window", "Taal": "Language",
        "Nederlands": "Dutch", "Engels": "English", "Help": "Help",
        "Snelgids": "Quick guide", "Over": "About",
        "Gereedschap": "Tools", "Potlood": "Pencil", "Penseel": "Brush",
        "Gum": "Eraser", "Vullen": "Fill", "Pipet": "Eyedropper",
        "Lijn": "Line", "Rechthoek": "Rectangle", "Ovaal": "Ellipse",
        "Afgeronde rechthoek": "Rounded rectangle", "Veelhoek": "Polygon",
        "Penseel: dekking": "Brush: opacity", "Penseel: zachtheid": "Brush: softness",
        "Afbeelding": "Image", "Bijsnijden tot selectie": "Crop to selection",
        "Formaat wijzigen...": "Resize...", "Canvasgrootte...": "Canvas size...",
        "Formaat wijzigen": "Resize", "Canvasgrootte": "Canvas size",
        "Verhouding behouden": "Keep ratio",
        "Draaien rechtsom": "Rotate right", "Draaien linksom": "Rotate left",
        "Spiegelen horizontaal": "Flip horizontal", "Spiegelen verticaal": "Flip vertical",
        "Maak eerst een selectie om op bij te snijden.":
            "Make a selection first to crop to.",
        "Tekst": "Text", "Verplaatsen": "Move", "Selecteren": "Select",
        "Lasso": "Lasso", "Knippen": "Cut", "Kopieren": "Copy", "Plakken": "Paste",
        "Lettertype": "Font",
        "Kleur": "Colour", "Grootte": "Size", "Gevuld": "Filled",
        "Transp. selectie": "Transp. select",
        "Achtergrondkleur wordt doorzichtig bij selecteren":
            "Background colour becomes transparent when selecting",
        "Kleur 1": "Colour 1", "Kleur 2": "Colour 2", "Wisselen": "Swap",
        "Voorgrond (linkermuisknop)": "Foreground (left mouse button)",
        "Achtergrond / gum (rechtermuisknop)": "Background / eraser (right mouse button)",
        "Lagen": "Layers", "Nieuwe laag": "New layer",
        "Laag verwijderen": "Delete layer", "Omhoog": "Up", "Omlaag": "Down",
        "Zichtbaar": "Visible", "Transparantie": "Opacity",
        "Naam wijzigen": "Rename", "Laag": "Layer",
        "Nieuw canvas": "New canvas", "Breedte": "Width", "Hoogte": "Height",
        "Maken": "Create", "Annuleren": "Cancel", "Achtergrond": "Background",
        "Wit": "White", "Transparant": "Transparent",
        "Type je tekst": "Type your text", "Donatie": "Donate",
        "Niet opgeslagen wijzigingen": "Unsaved changes",
        "Er zijn niet-opgeslagen wijzigingen. Toch doorgaan?":
            "There are unsaved changes. Continue anyway?",
        "Afbeeldingen": "Images", "Alle bestanden": "All files",
        "DravePaint-project": "DravePaint project",
        "Kon bestand niet openen": "Could not open file",
        "Kon niet opslaan": "Could not save",
        "Klaar": "Ready", "Opgeslagen": "Saved", "Geexporteerd": "Exported",
    }
}

def t(s):
    if LANG == "nl":
        return s
    return TRANSLATIONS.get(LANG, {}).get(s, s)


def set_lang(code):
    global LANG
    LANG = code


# ----------------------------------------------------------------------------- style
def stylesheet():
    return f"""
    QWidget {{ background:{BG}; color:{TEXT}; font-size:15px; }}
    QMainWindow {{ background:{BG}; }}
    QLabel {{ color:{TEXT}; }}
    QMenuBar {{ background:{PANEL}; color:{TEXT}; font-size:15px; }}
    QMenuBar::item:selected {{ background:{PANEL2}; }}
    QMenu {{ background:{PANEL}; color:{TEXT}; border:1px solid {LINE}; }}
    QMenu::item:selected {{ background:{ACCENT}; color:#0c1116; }}
    QStatusBar {{ background:{PANEL}; color:{MUTED}; font-size:14px; }}
    QPushButton {{ background:{PANEL2}; color:{TEXT}; border:1px solid {LINE};
        border-radius:8px; padding:9px 12px; font-size:15px; }}
    QPushButton:hover {{ border-color:{ACCENT}; }}
    QPushButton:checked {{ background:{ACCENT}; color:#0c1116; border:none; font-weight:bold; }}
    QPushButton#primary {{ background:{ACCENT}; color:#0c1116; border:none; font-weight:bold; }}
    QListWidget {{ background:{PANEL}; color:{TEXT}; border:1px solid {LINE};
        border-radius:8px; font-size:15px; }}
    QListWidget::item {{ padding:6px 4px; }}
    QListWidget::item:selected {{ background:{ACCENT}; color:#0c1116; }}
    QSlider::groove:horizontal {{ height:6px; background:{LINE}; border-radius:3px; }}
    QSlider::handle:horizontal {{ width:18px; background:{ACCENT}; border-radius:9px; margin:-7px 0; }}
    QSpinBox, QLineEdit, QComboBox {{ background:#e9e9e9; color:#111111;
        border:1px solid #9a9aa2; border-radius:6px; padding:6px 8px; font-size:15px; min-height:22px; }}
    QComboBox QAbstractItemView {{ background:#f2f2f0; color:#111111; selection-background-color:{ACCENT}; }}
    QScrollArea {{ background:{BG}; border:none; }}
    """


# ----------------------------------------------------------------------------- icon
def resource_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def app_icon():
    logo = resource_path(os.path.join("assets", "logo.png"))
    if os.path.exists(logo):
        ic = QIcon(logo)
        if not ic.isNull():
            return ic
    img = QImage(64, 64, QImage.Format.Format_ARGB32)
    img.fill(QColor(0, 0, 0, 0))
    p = QPainter(img)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    p.setBrush(QColor(PANEL2)); p.setPen(QColor(LINE))
    p.drawRoundedRect(4, 4, 56, 56, 12, 12)
    for col, cx in ((WARN, 22), (GOOD, 32), (ACCENT, 42)):
        p.setBrush(QColor(col)); p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPoint(cx, 30), 9, 9)
    p.setPen(QPen(QColor(TEXT), 3))
    p.drawLine(20, 46, 44, 46)
    p.end()
    return QIcon(QPixmap.fromImage(img))


# ----------------------------------------------------------------------------- image helpers
def qimage_to_pil(qimg):
    qimg = qimg.convertToFormat(QImage.Format.Format_RGBA8888)
    w, h = qimg.width(), qimg.height()
    ptr = qimg.bits(); ptr.setsize(h * w * 4)
    return Image.frombytes("RGBA", (w, h), bytes(ptr))


def pil_to_qimage(pil):
    pil = pil.convert("RGBA")
    data = pil.tobytes("raw", "RGBA")
    q = QImage(data, pil.width, pil.height, QImage.Format.Format_RGBA8888)
    return q.convertToFormat(QImage.Format.Format_ARGB32).copy()


def checker_brush(size=16):
    img = QImage(size * 2, size * 2, QImage.Format.Format_ARGB32)
    img.fill(QColor("#3a3a42"))
    p = QPainter(img)
    p.fillRect(0, 0, size, size, QColor("#2b2b31"))
    p.fillRect(size, size, size, size, QColor("#2b2b31"))
    p.end()
    return QBrush(QPixmap.fromImage(img))


# ----------------------------------------------------------------------------- model
class Layer:
    def __init__(self, width, height, name="Laag", fill=None, image=None):
        self.name = name
        self.visible = True
        self.opacity = 100  # 0..100
        if image is not None:
            self.image = image.convertToFormat(QImage.Format.Format_ARGB32)
        else:
            self.image = QImage(width, height, QImage.Format.Format_ARGB32)
            self.image.fill(fill if fill is not None else QColor(0, 0, 0, 0))

    def to_dict(self):
        from PyQt6.QtCore import QBuffer, QByteArray
        ba = QByteArray(); buf = QBuffer(ba); buf.open(QBuffer.OpenModeFlag.WriteOnly)
        self.image.save(buf, "PNG"); buf.close()
        return {"name": self.name, "visible": self.visible, "opacity": self.opacity,
                "png": base64.b64encode(bytes(ba)).decode("ascii")}

    @staticmethod
    def from_dict(d):
        raw = base64.b64decode(d["png"])
        img = QImage.fromData(raw, "PNG").convertToFormat(QImage.Format.Format_ARGB32)
        lay = Layer(img.width(), img.height(), d.get("name", "Laag"), image=img)
        lay.visible = d.get("visible", True)
        lay.opacity = d.get("opacity", 100)
        return lay


class Project:
    def __init__(self, width=1000, height=700, bg="white"):
        self.width = width
        self.height = height
        self.layers = []
        self.active = 0
        first = Layer(width, height, name="Achtergrond",
                      fill=QColor(255, 255, 255, 255) if bg == "white" else QColor(0, 0, 0, 0))
        self.layers.append(first)

    def active_layer(self):
        if 0 <= self.active < len(self.layers):
            return self.layers[self.active]
        return None

    def composite(self):
        out = QImage(self.width, self.height, QImage.Format.Format_ARGB32)
        out.fill(QColor(0, 0, 0, 0))
        p = QPainter(out)
        for lay in self.layers:
            if not lay.visible:
                continue
            p.setOpacity(max(0.0, min(1.0, lay.opacity / 100.0)))
            p.drawImage(0, 0, lay.image)
        p.end()
        return out

    # -- hele-afbeelding bewerkingen (alle lagen)
    def rotate90(self, clockwise=True):
        tr = QTransform().rotate(90 if clockwise else -90)
        for lay in self.layers:
            lay.image = lay.image.transformed(tr)
        self.width, self.height = self.height, self.width

    def flip(self, horizontal=True):
        tr = QTransform().scale(-1, 1) if horizontal else QTransform().scale(1, -1)
        for lay in self.layers:
            lay.image = lay.image.transformed(tr)

    def scale_to(self, w, h):
        w = max(1, int(w)); h = max(1, int(h))
        for lay in self.layers:
            lay.image = lay.image.scaled(w, h, Qt.AspectRatioMode.IgnoreAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation)
        self.width, self.height = w, h

    def resize_canvas(self, w, h):
        w = max(1, int(w)); h = max(1, int(h))
        for lay in self.layers:
            ni = QImage(w, h, QImage.Format.Format_ARGB32); ni.fill(QColor(0, 0, 0, 0))
            p = QPainter(ni); p.drawImage(0, 0, lay.image); p.end()
            lay.image = ni
        self.width, self.height = w, h

    def crop(self, rect):
        rect = rect.intersected(QRect(0, 0, self.width, self.height))
        if rect.width() < 1 or rect.height() < 1:
            return
        for lay in self.layers:
            lay.image = lay.image.copy(rect)
        self.width, self.height = rect.width(), rect.height()

    def to_dict(self):
        return {"app": APP_NAME, "version": APP_VERSION, "width": self.width,
                "height": self.height, "active": self.active,
                "layers": [l.to_dict() for l in self.layers]}

    @staticmethod
    def from_dict(d):
        pr = Project.__new__(Project)
        pr.width = d["width"]; pr.height = d["height"]
        pr.active = d.get("active", 0)
        pr.layers = [Layer.from_dict(x) for x in d["layers"]]
        if not pr.layers:
            pr.layers = [Layer(pr.width, pr.height, name="Achtergrond",
                               fill=QColor(255, 255, 255, 255))]
        pr.active = max(0, min(pr.active, len(pr.layers) - 1))
        return pr


# ----------------------------------------------------------------------------- canvas
class Canvas(QWidget):
    def __init__(self, project, window):
        super().__init__()
        self.project = project
        self.window = window
        self.zoom = 1.0
        self.tool = "pencil"
        self.fg = QColor(20, 20, 24)        # Kleur 1 (voorgrond)
        self.bg = QColor(255, 255, 255)     # Kleur 2 (achtergrond) - ook gum
        self._draw_col = self.fg
        self.size = 6
        self.fill_shapes = False
        self.brush_opacity = 100    # penseel-dekking 0..100
        self.brush_softness = 0     # penseel-zachtheid 0..100
        self._brush_buf = None      # losse buffer voor 1 penseelstreek
        self._brush_stamp = None
        self._poly_pts = None       # veelhoek-punten
        self._poly_cursor = None    # huidige muispositie voor live lijn
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._checker = checker_brush()
        self._drawing = False
        self._last = None
        self._start = None
        self._preview = None        # QImage overlay during shape drag
        self._move_orig = None      # original layer image when moving
        self._move_from = None
        # zwevende selectie (selecteren + slepen)
        self.sel_image = None       # QImage van het opgepakte stuk
        self.sel_rect = None        # QRect huidige positie (beeld-coords)
        self._sel_defining = False  # bezig met een nieuw kader te trekken
        self._sel_dragging = False  # bezig de zwevende selectie te verslepen
        self._sel_a = None          # startpunt kader
        self._sel_b = None          # huidig punt kader
        self._sel_grab = None       # greep-offset bij slepen
        self._lasso_pts = None      # punten tijdens lasso-tekenen
        self._clip = None           # klembord (geknipt/gekopieerd stuk)
        self.sel_transparent = True  # achtergrondkleur (Kleur 2) wordt doorzichtig bij selecteren
        self.undo_stack = []
        self.redo_stack = []
        self.dirty = False
        self._update_geometry()

    # -- project handling
    def set_project(self, project):
        self.project = project
        self.undo_stack.clear(); self.redo_stack.clear()
        self.dirty = False
        self.fit_to_window()
        self._update_geometry()
        self.update()
        self.window.refresh_layers()

    def _update_geometry(self):
        w = int(self.project.width * self.zoom)
        h = int(self.project.height * self.zoom)
        self.setMinimumSize(w + 40, h + 40)

    # -- undo
    def push_undo(self):
        idx = self.project.active
        lay = self.project.active_layer()
        if lay is None:
            return
        self.undo_stack.append((idx, lay.image.copy()))
        if len(self.undo_stack) > 30:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        self.dirty = True
        self.window.update_title()

    def undo(self):
        if not self.undo_stack:
            return
        entry = self.undo_stack.pop()
        if entry[0] == "PROJ":
            self.redo_stack.append(("PROJ", self._snapshot_project()))
            self._restore_project(entry[1])
        else:
            idx, img = entry
            if 0 <= idx < len(self.project.layers):
                self.redo_stack.append((idx, self.project.layers[idx].image.copy()))
                self.project.layers[idx].image = img
        self.update()

    def redo(self):
        if not self.redo_stack:
            return
        entry = self.redo_stack.pop()
        if entry[0] == "PROJ":
            self.undo_stack.append(("PROJ", self._snapshot_project()))
            self._restore_project(entry[1])
        else:
            idx, img = entry
            if 0 <= idx < len(self.project.layers):
                self.undo_stack.append((idx, self.project.layers[idx].image.copy()))
                self.project.layers[idx].image = img
        self.update()

    # -- volledige-project undo (voor draaien/spiegelen/schalen/bijsnijden)
    def _snapshot_project(self):
        return {"w": self.project.width, "h": self.project.height,
                "active": self.project.active,
                "layers": [(l.image.copy(), l.name, l.visible, l.opacity)
                           for l in self.project.layers]}

    def _restore_project(self, snap):
        self.project.width = snap["w"]; self.project.height = snap["h"]
        self.project.layers = []
        for img, name, vis, op in snap["layers"]:
            ly = Layer(snap["w"], snap["h"], name=name, image=img)
            ly.visible = vis; ly.opacity = op
            self.project.layers.append(ly)
        self.project.active = max(0, min(snap["active"], len(self.project.layers) - 1))
        self.sel_image = None; self.sel_rect = None
        self._update_geometry()
        self.window.refresh_layers()

    def push_project_undo(self):
        self.undo_stack.append(("PROJ", self._snapshot_project()))
        if len(self.undo_stack) > 30:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        self.dirty = True
        self.window.update_title()

    def apply_image_op(self, fn):
        """Voert een hele-afbeelding bewerking uit met undo + bijwerken."""
        self.commit_selection()
        self.push_project_undo()
        fn()
        self._update_geometry()
        self.window.refresh_layers()
        self.update()
        self.window.update_zoom_label()

    # -- zoom
    def set_zoom(self, z):
        self.zoom = max(0.1, min(16.0, z))
        self._update_geometry()
        self.update()
        self.window.update_zoom_label()

    def fit_to_window(self):
        area = self.parent()
        if area is None:
            return
        vw = max(50, area.width() - 60)
        vh = max(50, area.height() - 60)
        z = min(vw / self.project.width, vh / self.project.height)
        self.set_zoom(min(1.0, z) if z > 0 else 1.0)

    # -- coordinate mapping (widget -> image)
    def _offset(self):
        iw = self.project.width * self.zoom
        ih = self.project.height * self.zoom
        ox = max(20, (self.width() - iw) / 2)
        oy = max(20, (self.height() - ih) / 2)
        return ox, oy

    def _to_image(self, pos):
        ox, oy = self._offset()
        x = (pos.x() - ox) / self.zoom
        y = (pos.y() - oy) / self.zoom
        return QPoint(int(x), int(y))

    def _in_bounds(self, ip):
        return 0 <= ip.x() < self.project.width and 0 <= ip.y() < self.project.height

    # -- painting the widget
    def paintEvent(self, _e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(BG))
        ox, oy = self._offset()
        iw = int(self.project.width * self.zoom)
        ih = int(self.project.height * self.zoom)
        target = QRect(int(ox), int(oy), iw, ih)
        # checkerboard behind transparency
        p.fillRect(target, self._checker)
        comp = self.project.composite()
        if self._preview is not None:
            tmp = QImage(comp)
            pp = QPainter(tmp); pp.drawImage(0, 0, self._preview); pp.end()
            comp = tmp
        # zwevende selectie bovenop tonen
        if self.sel_image is not None and self.sel_rect is not None:
            tmp = QImage(comp)
            pp = QPainter(tmp); pp.drawImage(self.sel_rect.topLeft(), self.sel_image); pp.end()
            comp = tmp
        p.drawImage(target, comp)
        # marquee (selectiekader) - gestippeld, in schermcoords
        rect_to_show = None
        if self._sel_defining and self._sel_a is not None and self._sel_b is not None:
            rect_to_show = QRect(self._sel_a, self._sel_b).normalized()
        elif self.sel_rect is not None:
            rect_to_show = self.sel_rect
        if rect_to_show is not None:
            sx = int(ox + rect_to_show.x() * self.zoom)
            sy = int(oy + rect_to_show.y() * self.zoom)
            sw = int(rect_to_show.width() * self.zoom)
            sh = int(rect_to_show.height() * self.zoom)
            mr = QRect(sx, sy, sw, sh)
            p.setBrush(Qt.BrushStyle.NoBrush)
            pen = QPen(QColor(0, 0, 0), 1); pen.setStyle(Qt.PenStyle.DashLine)
            p.setPen(pen); p.drawRect(mr)
            pen2 = QPen(QColor(255, 255, 255), 1); pen2.setStyle(Qt.PenStyle.DashLine)
            pen2.setDashOffset(3); p.setPen(pen2); p.drawRect(mr)
        # lasso-lijn tonen tijdens tekenen
        if self._lasso_pts and len(self._lasso_pts) > 1:
            scr = QPolygon([QPoint(int(ox + pt.x() * self.zoom), int(oy + pt.y() * self.zoom))
                            for pt in self._lasso_pts])
            p.setBrush(Qt.BrushStyle.NoBrush)
            pen = QPen(QColor(0, 0, 0), 1); pen.setStyle(Qt.PenStyle.DashLine)
            p.setPen(pen); p.drawPolyline(scr)
            pen2 = QPen(QColor(255, 255, 255), 1); pen2.setStyle(Qt.PenStyle.DashLine)
            pen2.setDashOffset(3); p.setPen(pen2); p.drawPolyline(scr)
        # veelhoek-lijn tonen tijdens plaatsen
        if self._poly_pts:
            pts = list(self._poly_pts)
            if self._poly_cursor is not None:
                pts = pts + [self._poly_cursor]
            scr = QPolygon([QPoint(int(ox + pt.x() * self.zoom), int(oy + pt.y() * self.zoom))
                            for pt in pts])
            p.setBrush(Qt.BrushStyle.NoBrush)
            pen = QPen(QColor(self._draw_col.red(), self._draw_col.green(), self._draw_col.blue()), 1)
            pen.setStyle(Qt.PenStyle.DashLine); p.setPen(pen); p.drawPolyline(scr)
            # puntjes op de hoekpunten
            p.setBrush(QColor(255, 255, 255)); p.setPen(QPen(QColor(0, 0, 0), 1))
            for q in scr:
                p.drawEllipse(q, 3, 3)
        # border
        p.setPen(QPen(QColor(LINE), 1)); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(target)
        p.end()

    # -- selectie (selecteren + slepen)
    def commit_selection(self):
        """Plaats de zwevende selectie definitief op de laag."""
        if self.sel_image is None or self.sel_rect is None:
            return
        lay = self.project.active_layer()
        if lay is not None:
            pp = QPainter(lay.image)
            pp.drawImage(self.sel_rect.topLeft(), self.sel_image)
            pp.end()
        self.sel_image = None
        self.sel_rect = None
        self._sel_dragging = False
        self.update()

    def copy_selection(self):
        if self.sel_image is not None:
            self._clip = self.sel_image.copy()
            try:
                QApplication.clipboard().setImage(self._clip)
            except Exception:
                pass
            return True
        return False

    def cut_selection(self):
        if self.sel_image is not None:
            self.copy_selection()
            # het zwevende stuk is al uit de laag geknipt -> simpelweg weggooien
            self.sel_image = None
            self.sel_rect = None
            self.dirty = True
            self.window.update_title()
            self.update()
            return True
        return False

    def paste(self):
        img = self._clip
        if img is None or img.isNull():
            try:
                cb = QApplication.clipboard().image()
                if cb is not None and not cb.isNull():
                    img = cb.convertToFormat(QImage.Format.Format_ARGB32)
            except Exception:
                img = None
        if img is None or img.isNull():
            return False
        self.commit_selection()
        self.window.select_tool("select")
        self.sel_image = img.copy()
        self.sel_rect = QRect(10, 10, img.width(), img.height())
        self.dirty = True
        self.window.update_title()
        self.update()
        return True

    def _apply_bg_transparency(self, piece):
        """Maakt pixels met de achtergrondkleur (Kleur 2) doorzichtig in een selectie-stuk."""
        if not (self.sel_transparent and HAVE_PIL):
            return piece
        try:
            from PIL import ImageChops
            pil = qimage_to_pil(piece)
            r, g, b, a = pil.split()
            rgb = Image.merge("RGB", (r, g, b))
            bg_img = Image.new("RGB", pil.size, (self.bg.red(), self.bg.green(), self.bg.blue()))
            diff = ImageChops.difference(rgb, bg_img)
            dr, dg, db = diff.split()
            dmax = ImageChops.lighter(ImageChops.lighter(dr, dg), db)
            keep = dmax.point(lambda v: 255 if v > 40 else 0)
            new_a = ImageChops.multiply(a, keep)
            pil.putalpha(new_a)
            return pil_to_qimage(pil)
        except Exception:
            return piece

    def _lift_selection(self, rect):
        """Knip een rechthoekig gebied uit de actieve laag in een zwevende selectie."""
        lay = self.project.active_layer()
        if lay is None:
            return
        rect = rect.intersected(QRect(0, 0, self.project.width, self.project.height))
        if rect.width() < 2 or rect.height() < 2:
            return
        self.push_undo()
        piece = self._apply_bg_transparency(lay.image.copy(rect))
        self.sel_image = piece
        pp = QPainter(lay.image)
        pp.fillRect(rect, self.bg)              # gat vullen met Kleur 2
        pp.end()
        self.sel_rect = QRect(rect)
        self.update()

    def _lift_lasso(self, points):
        """Knip een vrije-vorm (lasso) gebied uit de actieve laag."""
        lay = self.project.active_layer()
        if lay is None or len(points) < 3:
            return
        poly = QPolygon([QPoint(p.x(), p.y()) for p in points])
        rect = poly.boundingRect().intersected(QRect(0, 0, self.project.width, self.project.height))
        if rect.width() < 2 or rect.height() < 2:
            return
        self.push_undo()
        piece = lay.image.copy(rect)
        # masker: alles buiten de lasso doorzichtig maken
        mask = QImage(rect.size(), QImage.Format.Format_ARGB32)
        mask.fill(QColor(0, 0, 0, 0))
        mp = QPainter(mask)
        mp.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        mp.translate(-rect.x(), -rect.y())
        mp.setBrush(QColor(255, 255, 255, 255)); mp.setPen(Qt.PenStyle.NoPen)
        mp.drawPolygon(poly)
        mp.end()
        pp = QPainter(piece)
        pp.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
        pp.drawImage(0, 0, mask)
        pp.end()
        piece = self._apply_bg_transparency(piece)
        self.sel_image = piece
        # gat (binnen de lasso) vullen met Kleur 2
        cp = QPainter(lay.image)
        cp.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        cp.setBrush(self.bg); cp.setPen(Qt.PenStyle.NoPen)
        cp.drawPolygon(poly)
        cp.end()
        self.sel_rect = QRect(rect)
        self.update()

    # -- drawing helpers
    def _pen(self, col):
        pen = QPen(col, self.size)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        return pen

    def _draw_line_on(self, img, a, b, color):
        pp = QPainter(img)
        pp.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        pen = QPen(color, self.size)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pp.setPen(pen)
        pp.drawLine(a, b)
        pp.end()

    # -- zacht penseel (dekking + zachtheid) via aparte streek-buffer
    def _make_stamp(self, col):
        s = max(1, self.size)
        img = QImage(s, s, QImage.Format.Format_ARGB32)
        img.fill(QColor(0, 0, 0, 0))
        p = QPainter(img)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setPen(Qt.PenStyle.NoPen)
        soft = self.brush_softness / 100.0
        if soft <= 0.01:
            p.setBrush(QColor(col.red(), col.green(), col.blue(), 255))
            p.drawEllipse(0, 0, s, s)
        else:
            grad = QRadialGradient(s / 2.0, s / 2.0, s / 2.0)
            inner = max(0.0, 1.0 - soft)
            grad.setColorAt(0.0, QColor(col.red(), col.green(), col.blue(), 255))
            grad.setColorAt(inner, QColor(col.red(), col.green(), col.blue(), 255))
            grad.setColorAt(1.0, QColor(col.red(), col.green(), col.blue(), 0))
            p.setBrush(QBrush(grad))
            p.drawEllipse(0, 0, s, s)
        p.end()
        return img

    def _stamp_line(self, buf, a, b):
        if self._brush_stamp is None:
            return
        s = self._brush_stamp.width()
        dx = b.x() - a.x(); dy = b.y() - a.y()
        dist = max(1, int((dx * dx + dy * dy) ** 0.5))
        step = max(1, s // 5)
        n = max(1, dist // step)
        p = QPainter(buf)
        for i in range(n + 1):
            f = i / n
            x = a.x() + dx * f - s / 2.0
            y = a.y() + dy * f - s / 2.0
            p.drawImage(int(round(x)), int(round(y)), self._brush_stamp)
        p.end()

    def _refresh_brush_preview(self):
        """Toont de lopende penseelstreek met de juiste dekking."""
        if self._brush_buf is None:
            return
        self._preview = QImage(self.project.width, self.project.height,
                               QImage.Format.Format_ARGB32)
        self._preview.fill(QColor(0, 0, 0, 0))
        pp = QPainter(self._preview)
        pp.setOpacity(self.brush_opacity / 100.0)
        pp.drawImage(0, 0, self._brush_buf)
        pp.end()

    def _flood_fill(self, ip, col):
        lay = self.project.active_layer()
        if lay is None or not HAVE_PIL:
            return
        self.push_undo()
        pil = qimage_to_pil(lay.image)
        try:
            ImageDraw.floodfill(pil, (ip.x(), ip.y()),
                                (col.red(), col.green(), col.blue(), 255), thresh=40)
        except Exception:
            pass
        lay.image = pil_to_qimage(pil)
        self.update()

    def _pick_color(self, ip, to_bg=False):
        comp = self.project.composite()
        if self._in_bounds(ip):
            c = comp.pixelColor(ip)
            if c.alpha() > 0:
                picked = QColor(c.red(), c.green(), c.blue())
                if to_bg:
                    self.bg = picked
                else:
                    self.fg = picked
                self.window.update_color_buttons()

    def _place_text(self, ip):
        dlg = TextDialog(self, base_size=max(12, self.size * 4))
        if not dlg.exec():
            return
        text, font = dlg.result()
        if not text:
            return
        lay = self.project.active_layer()
        if lay is None:
            return
        self.push_undo()
        pp = QPainter(lay.image)
        pp.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        pp.setFont(font); pp.setPen(self.fg)
        pp.drawText(QPoint(ip.x(), ip.y()), text)
        pp.end()
        self.update()

    # -- mouse
    def mousePressEvent(self, e):
        if e.button() not in (Qt.MouseButton.LeftButton, Qt.MouseButton.RightButton):
            return
        right = e.button() == Qt.MouseButton.RightButton
        col = self.bg if right else self.fg
        self._draw_col = col
        ip = self._to_image(e.position().toPoint())
        lay = self.project.active_layer()
        if lay is None:
            return
        if self.tool == "fill":
            if self._in_bounds(ip):
                self._flood_fill(ip, col)
            return
        if self.tool == "eyedropper":
            self._pick_color(ip, to_bg=right); return
        if self.tool == "text":
            if self._in_bounds(ip):
                self._place_text(ip)
            return
        if self.tool == "move":
            self.push_undo()
            self._move_orig = lay.image.copy()
            self._move_from = ip
            self._drawing = True
            return
        if self.tool in ("select", "lasso"):
            # binnen bestaande zwevende selectie? -> verslepen
            if self.sel_image is not None and self.sel_rect is not None and self.sel_rect.contains(ip):
                self._sel_dragging = True
                self._sel_grab = QPoint(ip.x() - self.sel_rect.x(), ip.y() - self.sel_rect.y())
                return
            # anders: bestaande selectie vastzetten en een nieuwe beginnen
            self.commit_selection()
            if self.tool == "select":
                self._sel_defining = True
                self._sel_a = ip
                self._sel_b = ip
            else:  # lasso
                self._lasso_pts = [ip]
            self.update()
            return
        if self.tool == "polygon":
            if right:
                self._finish_polygon()
                return
            self._draw_col = self.fg
            if self._poly_pts is None:
                self._poly_pts = [ip]
            else:
                self._poly_pts.append(ip)
            self._poly_cursor = ip
            self.update()
            return
        if self.tool == "brush":
            self.push_undo()
            self._drawing = True
            self._last = ip
            self._draw_col = col
            self._brush_buf = QImage(self.project.width, self.project.height,
                                     QImage.Format.Format_ARGB32)
            self._brush_buf.fill(QColor(0, 0, 0, 0))
            self._brush_stamp = self._make_stamp(col)
            self._stamp_line(self._brush_buf, ip, ip)
            self._refresh_brush_preview()
            self.update()
            return
        if self.tool in ("pencil", "eraser"):
            self.push_undo()
            self._drawing = True
            self._last = ip
            draw_col = self.bg if self.tool == "eraser" else col
            self._draw_col = draw_col
            self._draw_line_on(lay.image, ip, ip, draw_col)
            self.update()
            return
        if self.tool in ("line", "rectangle", "ellipse", "roundrect"):
            self.push_undo()
            self._drawing = True
            self._start = ip
            self._preview = QImage(self.project.width, self.project.height,
                                   QImage.Format.Format_ARGB32)
            self._preview.fill(QColor(0, 0, 0, 0))
            return

    def mouseMoveEvent(self, e):
        ip = self._to_image(e.position().toPoint())
        self.window.update_pos_label(ip)
        # selecteren/lasso heeft eigen sleep-status (los van _drawing)
        if self.tool in ("select", "lasso"):
            if self._sel_defining:
                self._sel_b = ip
                self.update()
                return
            if self._lasso_pts is not None:
                self._lasso_pts.append(ip)
                self.update()
                return
            if self._sel_dragging and self.sel_rect is not None:
                nx = ip.x() - self._sel_grab.x()
                ny = ip.y() - self._sel_grab.y()
                self.sel_rect = QRect(nx, ny, self.sel_rect.width(), self.sel_rect.height())
                self.update()
                return
        # veelhoek: live lijn naar de cursor
        if self.tool == "polygon" and self._poly_pts is not None:
            self._poly_cursor = ip
            self.update()
            return
        if not self._drawing:
            return
        lay = self.project.active_layer()
        if lay is None:
            return
        if self.tool == "brush" and self._last is not None and self._brush_buf is not None:
            self._stamp_line(self._brush_buf, self._last, ip)
            self._last = ip
            self._refresh_brush_preview()
            self.update()
        elif self.tool in ("pencil", "eraser") and self._last is not None:
            self._draw_line_on(lay.image, self._last, ip, self._draw_col)
            self._last = ip
            self.update()
        elif self.tool == "move" and self._move_orig is not None:
            dx = ip.x() - self._move_from.x()
            dy = ip.y() - self._move_from.y()
            moved = QImage(self.project.width, self.project.height,
                           QImage.Format.Format_ARGB32)
            moved.fill(QColor(0, 0, 0, 0))
            pp = QPainter(moved); pp.drawImage(QPoint(dx, dy), self._move_orig); pp.end()
            lay.image = moved
            self.update()
        elif self.tool in ("line", "rectangle", "ellipse", "roundrect") and self._start is not None:
            self._preview.fill(QColor(0, 0, 0, 0))
            pp = QPainter(self._preview)
            pp.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            pp.setPen(self._pen(self._draw_col))
            if self.fill_shapes and self.tool in ("rectangle", "ellipse", "roundrect"):
                pp.setBrush(self._draw_col)
            else:
                pp.setBrush(Qt.BrushStyle.NoBrush)
            a, b = self._start, ip
            if self.tool == "line":
                pp.drawLine(a, b)
            else:
                r = QRect(a, b).normalized()
                if self.tool == "rectangle":
                    pp.drawRect(r)
                elif self.tool == "roundrect":
                    rad = max(4, min(r.width(), r.height()) // 6)
                    pp.drawRoundedRect(r, rad, rad)
                else:
                    pp.drawEllipse(r)
            pp.end()
            self.update()

    def mouseReleaseEvent(self, e):
        if self.tool in ("select", "lasso"):
            if self._sel_defining:
                self._sel_defining = False
                if self._sel_a is not None and self._sel_b is not None:
                    rect = QRect(self._sel_a, self._sel_b).normalized()
                    self._sel_a = None; self._sel_b = None
                    self._lift_selection(rect)
                return
            if self._lasso_pts is not None:
                pts = self._lasso_pts
                self._lasso_pts = None
                self._lift_lasso(pts)
                return
            if self._sel_dragging:
                self._sel_dragging = False
                self.dirty = True
                self.window.update_title()
                return
        if not self._drawing:
            return
        self._drawing = False
        lay = self.project.active_layer()
        if self.tool in ("line", "rectangle", "ellipse", "roundrect") and self._preview is not None and lay is not None:
            pp = QPainter(lay.image); pp.drawImage(0, 0, self._preview); pp.end()
        if self.tool == "brush" and self._brush_buf is not None and lay is not None:
            pp = QPainter(lay.image)
            pp.setOpacity(self.brush_opacity / 100.0)
            pp.drawImage(0, 0, self._brush_buf)
            pp.end()
        self._brush_buf = None
        self._brush_stamp = None
        self._preview = None
        self._start = None
        self._last = None
        self._move_orig = None
        self.update()

    def mouseDoubleClickEvent(self, e):
        if self.tool == "polygon":
            self._finish_polygon()

    def _finish_polygon(self):
        pts = self._poly_pts
        self._poly_pts = None
        self._poly_cursor = None
        if not pts or len(pts) < 2:
            self.update(); return
        lay = self.project.active_layer()
        if lay is None:
            self.update(); return
        self.push_undo()
        poly = QPolygon([QPoint(p.x(), p.y()) for p in pts])
        pp = QPainter(lay.image)
        pp.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        pp.setPen(self._pen(self._draw_col))
        pp.setBrush(self._draw_col if self.fill_shapes else Qt.BrushStyle.NoBrush)
        pp.drawPolygon(poly)
        pp.end()
        self.update()

    def keyPressEvent(self, e):
        k = e.key()
        if self.tool == "polygon" and self._poly_pts is not None:
            if k in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self._finish_polygon(); return
            if k == Qt.Key.Key_Escape:
                self._poly_pts = None; self._poly_cursor = None; self.update(); return
        if self.sel_image is not None:
            if k in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Escape):
                self.commit_selection(); return
            if k in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
                # zwevende selectie weggooien (was al uit de laag geknipt)
                self.sel_image = None; self.sel_rect = None
                self.dirty = True; self.window.update_title(); self.update(); return
        super().keyPressEvent(e)


# ----------------------------------------------------------------------------- new canvas dialog
class NewCanvasDialog(QDialog):
    def __init__(self, parent, w=1000, h=700):
        super().__init__(parent)
        self.setWindowTitle(t("Nieuw canvas")); self.setWindowIcon(app_icon())
        self.setStyleSheet(stylesheet()); self.setMinimumWidth(360)
        lay = QVBoxLayout(self); lay.setContentsMargins(20, 20, 20, 20); lay.setSpacing(12)
        grid = QGridLayout(); grid.setHorizontalSpacing(10); grid.setVerticalSpacing(10)
        self.sp_w = QSpinBox(); self.sp_w.setRange(1, 10000); self.sp_w.setValue(w)
        self.sp_h = QSpinBox(); self.sp_h.setRange(1, 10000); self.sp_h.setValue(h)
        self.bg = QComboBox(); self.bg.addItem(t("Wit"), "white"); self.bg.addItem(t("Transparant"), "transparent")
        grid.addWidget(QLabel(t("Breedte")), 0, 0); grid.addWidget(self.sp_w, 0, 1)
        grid.addWidget(QLabel(t("Hoogte")), 1, 0); grid.addWidget(self.sp_h, 1, 1)
        grid.addWidget(QLabel(t("Achtergrond")), 2, 0); grid.addWidget(self.bg, 2, 1)
        lay.addLayout(grid)
        row = QHBoxLayout()
        ok = QPushButton(t("Maken")); ok.setObjectName("primary"); ok.setMinimumHeight(42)
        ok.clicked.connect(self.accept)
        cancel = QPushButton(t("Annuleren")); cancel.setMinimumHeight(42)
        cancel.clicked.connect(self.reject)
        row.addWidget(cancel); row.addWidget(ok)
        lay.addLayout(row)

    def values(self):
        return self.sp_w.value(), self.sp_h.value(), self.bg.currentData()


class ResizeDialog(QDialog):
    """Nieuwe breedte/hoogte kiezen (met optie verhouding behouden)."""
    def __init__(self, parent, w, h, title):
        super().__init__(parent)
        self.setWindowTitle(title); self.setWindowIcon(app_icon())
        self.setStyleSheet(stylesheet()); self.setMinimumWidth(360)
        self._ratio = (w / h) if h else 1.0
        self._guard = False
        lay = QVBoxLayout(self); lay.setContentsMargins(20, 20, 20, 20); lay.setSpacing(12)
        grid = QGridLayout(); grid.setHorizontalSpacing(10); grid.setVerticalSpacing(10)
        self.sp_w = QSpinBox(); self.sp_w.setRange(1, 10000); self.sp_w.setValue(w)
        self.sp_h = QSpinBox(); self.sp_h.setRange(1, 10000); self.sp_h.setValue(h)
        grid.addWidget(QLabel(t("Breedte")), 0, 0); grid.addWidget(self.sp_w, 0, 1)
        grid.addWidget(QLabel(t("Hoogte")), 1, 0); grid.addWidget(self.sp_h, 1, 1)
        lay.addLayout(grid)
        self.keep = QCheckBox(t("Verhouding behouden")); self.keep.setChecked(True)
        lay.addWidget(self.keep)
        self.sp_w.valueChanged.connect(self._w_changed)
        self.sp_h.valueChanged.connect(self._h_changed)
        row = QHBoxLayout()
        ok = QPushButton("OK"); ok.setObjectName("primary"); ok.setMinimumHeight(42)
        ok.clicked.connect(self.accept)
        cancel = QPushButton(t("Annuleren")); cancel.setMinimumHeight(42)
        cancel.clicked.connect(self.reject)
        row.addWidget(cancel); row.addWidget(ok)
        lay.addLayout(row)

    def _w_changed(self, v):
        if self._guard or not self.keep.isChecked():
            return
        self._guard = True
        self.sp_h.setValue(max(1, round(v / self._ratio)))
        self._guard = False

    def _h_changed(self, v):
        if self._guard or not self.keep.isChecked():
            return
        self._guard = True
        self.sp_w.setValue(max(1, round(v * self._ratio)))
        self._guard = False

    def values(self):
        return self.sp_w.value(), self.sp_h.value()


# ----------------------------------------------------------------------------- quick guide / about
class TextDialog(QDialog):
    """Tekst typen + lettertype, grootte, vet/cursief kiezen."""
    def __init__(self, parent, base_size=24):
        super().__init__(parent)
        self.setWindowTitle(t("Tekst")); self.setWindowIcon(app_icon())
        self.setStyleSheet(stylesheet()); self.setMinimumWidth(420)
        lay = QVBoxLayout(self); lay.setContentsMargins(20, 18, 20, 18); lay.setSpacing(10)
        lay.addWidget(QLabel(t("Type je tekst")))
        self.edit = QLineEdit()
        lay.addWidget(self.edit)
        lay.addWidget(QLabel(t("Lettertype")))
        self.font_combo = QFontComboBox()
        lay.addWidget(self.font_combo)
        row = QHBoxLayout(); row.setSpacing(8)
        row.addWidget(QLabel(t("Grootte")))
        self.size = QSpinBox(); self.size.setRange(6, 400); self.size.setValue(base_size)
        row.addWidget(self.size)
        self.bold = QPushButton("B"); self.bold.setCheckable(True); self.bold.setFixedWidth(44)
        self.bold.setStyleSheet("font-weight:bold;")
        self.italic = QPushButton("I"); self.italic.setCheckable(True); self.italic.setFixedWidth(44)
        self.italic.setStyleSheet("font-style:italic;")
        row.addWidget(self.bold); row.addWidget(self.italic); row.addStretch(1)
        lay.addLayout(row)
        btns = QHBoxLayout()
        cancel = QPushButton(t("Annuleren")); cancel.setMinimumHeight(40); cancel.clicked.connect(self.reject)
        ok = QPushButton("OK"); ok.setObjectName("primary"); ok.setMinimumHeight(40); ok.clicked.connect(self.accept)
        btns.addWidget(cancel); btns.addWidget(ok)
        lay.addLayout(btns)
        self.edit.setFocus()

    def result(self):
        f = self.font_combo.currentFont()
        f.setPixelSize(self.size.value())
        f.setBold(self.bold.isChecked())
        f.setItalic(self.italic.isChecked())
        return self.edit.text(), f


class GuideDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle(t("Snelgids")); self.setWindowIcon(app_icon())
        self.setStyleSheet(stylesheet()); self.setMinimumSize(560, 460)
        from PyQt6.QtWidgets import QTextBrowser
        lay = QVBoxLayout(self); lay.setContentsMargins(22, 18, 22, 18); lay.setSpacing(12)
        title = QLabel(f"{APP_NAME} - {t('Snelgids')}")
        title.setStyleSheet("font-size:20px;font-weight:bold;color:#ffffff;")
        tb = QTextBrowser()
        if LANG == "nl":
            tb.setHtml(
                "<p><b>Gereedschap</b> kies je links: potlood, penseel, gum, vullen, "
                "pipet, lijn, rechthoek, ovaal, tekst en verplaatsen.</p>"
                "<p><b>Twee kleuren</b>: Kleur 1 is de voorgrond (linkermuisknop), "
                "Kleur 2 de achtergrond (rechtermuisknop). De <b>Gum</b> schildert met "
                "Kleur 2. Met <b>Wisselen</b> verwissel je beide.</p>"
                "<p><b>Grootte</b> stel je met de schuif in. Vink <b>Gevuld</b> "
                "aan om rechthoek/ovaal te vullen.</p>"
                "<p><b>Lagen</b> staan rechts. Maak nieuwe lagen, sleep ze omhoog/omlaag, "
                "zet ze zichtbaar/onzichtbaar en regel de transparantie. Je tekent altijd "
                "op de <b>geselecteerde</b> laag.</p>"
                "<p><b>Vullen</b> werkt binnen gelijke kleuren rond waar je klikt. "
                "<b>Pipet</b> pakt een kleur van het beeld. <b>Verplaatsen</b> schuift de "
                "hele actieve laag.</p>"
                "<p><b>Selecteren</b>: trek een kader om een stuk; dat wordt opgepakt en kun "
                "je naar een eigen plek <b>slepen</b>. Met <b>Lasso</b> selecteer je een "
                "vrije vorm. Enter of een ander gereedschap zet het vast, Delete gooit het weg. "
                "Met <b>Knippen/Kopieren/Plakken</b> (Ctrl+X / Ctrl+C / Ctrl+V) verplaats of "
                "dupliceer je een selectie.</p>"
                "<p><b>Tekst</b>: klik op het canvas en kies je <b>lettertype</b>, grootte en "
                "vet/cursief.</p>"
                "<p><b>Openen</b> kan elk gangbaar type (PNG, JPG, BMP, GIF, WEBP, TIFF). "
                "Bewaar je werk als <b>.dravepaint</b>-project (met lagen) of exporteer naar "
                "een platte afbeelding.</p>"
                "<p>Ctrl+Z = ongedaan, Ctrl+Y = opnieuw. Plus/min = zoomen.</p>"
                "<p>Onder de kleurknoppen staat een <b>kleurenpalet</b>: klik = Kleur 1, "
                "rechtsklik = Kleur 2. Via menu <b>Afbeelding</b> kun je draaien, spiegelen, "
                "het formaat wijzigen, de canvasgrootte aanpassen en bijsnijden tot een "
                "selectie.</p>"
                "<p>Het <b>Penseel</b> heeft schuifjes voor <b>dekking</b> en <b>zachtheid</b>. "
                "Met de <b>Veelhoek</b> klik je hoekpunten; dubbelklik of rechtsklik sluit de "
                "vorm (Enter sluit ook, Esc annuleert).</p>")
        else:
            tb.setHtml(
                "<p>Pick a <b>tool</b> on the left: pencil, brush, eraser, fill, "
                "eyedropper, line, rectangle, ellipse, text and move.</p>"
                "<p><b>Two colours</b>: Colour 1 is the foreground (left mouse button), "
                "Colour 2 the background (right mouse button). The <b>Eraser</b> paints "
                "with Colour 2. <b>Swap</b> exchanges them.</p>"
                "<p>Set <b>Size</b> with the slider. Tick <b>Filled</b> to fill "
                "rectangle/ellipse.</p>"
                "<p><b>Layers</b> are on the right. Add layers, move them up/down, toggle "
                "visibility and set opacity. You always draw on the <b>selected</b> layer.</p>"
                "<p><b>Fill</b> floods similar colours around the click. <b>Eyedropper</b> "
                "picks a colour. <b>Move</b> shifts the whole active layer.</p>"
                "<p><b>Select</b>: drag a box around an area; it is lifted and you can "
                "<b>drag</b> it to its own spot. Use <b>Lasso</b> for a free-form selection. "
                "Enter or another tool drops it, Delete discards it. Use "
                "<b>Cut/Copy/Paste</b> (Ctrl+X / Ctrl+C / Ctrl+V) to move or duplicate a "
                "selection.</p>"
                "<p><b>Text</b>: click the canvas and choose your <b>font</b>, size and "
                "bold/italic.</p>"
                "<p><b>Open</b> any common type (PNG, JPG, BMP, GIF, WEBP, TIFF). Save your "
                "work as a <b>.dravepaint</b> project (with layers) or export to a flat image.</p>"
                "<p>Ctrl+Z = undo, Ctrl+Y = redo. Plus/minus = zoom.</p>")
        ok = QPushButton("OK"); ok.setObjectName("primary"); ok.setMinimumHeight(42)
        ok.clicked.connect(self.accept)
        lay.addWidget(title); lay.addWidget(tb, 1); lay.addWidget(ok)


# ----------------------------------------------------------------------------- main window
TOOLS = [
    ("pencil", "Potlood"), ("brush", "Penseel"), ("eraser", "Gum"),
    ("fill", "Vullen"), ("eyedropper", "Pipet"), ("line", "Lijn"),
    ("rectangle", "Rechthoek"), ("roundrect", "Afgeronde rechthoek"), ("ellipse", "Ovaal"),
    ("polygon", "Veelhoek"), ("text", "Tekst"),
    ("select", "Selecteren"), ("lasso", "Lasso"), ("move", "Verplaatsen"),
]
TOOL_ICONS = {
    "pencil": "✏", "brush": "🖌", "eraser": "⌫", "fill": "🪣", "eyedropper": "💧",
    "line": "／", "rectangle": "▭", "roundrect": "▢", "ellipse": "◯", "polygon": "⬠", "text": "T", "move": "✥",
    "select": "⛶", "lasso": "✐",
}


PALETTE = [
    "#000000", "#444444", "#888888", "#cccccc", "#ffffff", "#7a4a1e",
    "#e02020", "#f07a00", "#f5d000", "#3fae3f", "#1e8fae", "#2050d0",
    "#7a3fd0", "#d040a0", "#f29bc0", "#9fd4ff", "#bff0bf", "#fff0a0",
]


class SwatchButton(QPushButton):
    """Kleurvakje: linkermuis = Kleur 1, rechtermuis = Kleur 2."""
    def __init__(self, color, on_pick):
        super().__init__()
        self._color = QColor(color)
        self._on_pick = on_pick
        self.setFixedSize(24, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(self._color.name() + "  (rechtsklik = Kleur 2)")
        self.setStyleSheet(
            f"background:{self._color.name()}; border:1px solid {LINE}; border-radius:5px;")

    def mousePressEvent(self, e):
        self._on_pick(self._color, e.button() == Qt.MouseButton.RightButton)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(app_icon())
        self.setStyleSheet(stylesheet())
        self.resize(1280, 820)
        self.project = Project(1000, 700, "white")
        self.path = None
        self.tool_buttons = {}

        # central: canvas in scroll area
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(False)
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.canvas = Canvas(self.project, self)
        self.scroll.setWidget(self.canvas)

        # left tool panel (scrollbaar zodat niets wegvalt)
        left = self._build_tools()
        left_scroll = QScrollArea()
        left_scroll.setWidget(left)
        left_scroll.setWidgetResizable(True)
        left_scroll.setFixedWidth(214)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_scroll.setFrameShape(QFrame.Shape.NoFrame)
        # right layers panel
        right = self._build_layers()

        central = QWidget(); h = QHBoxLayout(central)
        h.setContentsMargins(8, 8, 8, 8); h.setSpacing(8)
        h.addWidget(left_scroll)
        h.addWidget(self.scroll, 1)
        h.addWidget(right)
        self.setCentralWidget(central)

        self._build_menu()
        self.setStatusBar(QStatusBar())
        self.pos_label = QLabel("")
        self.zoom_label = QLabel("100%")
        self.statusBar().addPermanentWidget(self.pos_label)
        self.statusBar().addPermanentWidget(self.zoom_label)
        self.statusBar().addPermanentWidget(QLabel(f"v{APP_VERSION}"))
        self.statusBar().showMessage(t("Klaar"))

        self.select_tool("pencil")
        self.update_color_buttons()
        self.refresh_layers()
        self.update_title()

    # -- tool panel
    def _build_tools(self):
        w = QWidget(); w.setFixedWidth(196)
        v = QVBoxLayout(w); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(6)
        row_ur = QHBoxLayout(); row_ur.setSpacing(6)
        self.undo_btn = QPushButton("\u21b6"); self.undo_btn.setToolTip(t("Ongedaan maken"))
        self.undo_btn.setMinimumHeight(40)
        self.undo_btn.clicked.connect(self.canvas.undo)
        self.redo_btn = QPushButton("\u21b7"); self.redo_btn.setToolTip(t("Opnieuw"))
        self.redo_btn.setMinimumHeight(40)
        self.redo_btn.clicked.connect(self.canvas.redo)
        row_ur.addWidget(self.undo_btn); row_ur.addWidget(self.redo_btn)
        v.addLayout(row_ur)
        lbl = QLabel(t("Gereedschap")); lbl.setStyleSheet("font-weight:bold;")
        v.addWidget(lbl)
        short = {"roundrect": ("Afgerond" if LANG == "nl" else "Rounded")}
        grid = QGridLayout(); grid.setSpacing(5)
        grid.setColumnStretch(0, 1); grid.setColumnStretch(1, 1)
        for i, (key, name) in enumerate(TOOLS):
            label = short.get(key, t(name))
            b = QPushButton(TOOL_ICONS.get(key, "") + " " + label)
            b.setCheckable(True); b.setMinimumHeight(38)
            b.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
            b.setStyleSheet("text-align:left; padding-left:8px;")
            b.clicked.connect(lambda _c, k=key: self.select_tool(k))
            b.setToolTip(t(name))
            self.tool_buttons[key] = b
            grid.addWidget(b, i // 2, i % 2)
        v.addLayout(grid)
        v.addSpacing(6)
        self.fg_btn = QPushButton(t("Kleur 1")); self.fg_btn.setMinimumHeight(38)
        self.fg_btn.setToolTip(t("Voorgrond (linkermuisknop)"))
        self.fg_btn.clicked.connect(lambda: self.pick_color(False))
        self.bg_btn = QPushButton(t("Kleur 2")); self.bg_btn.setMinimumHeight(38)
        self.bg_btn.setToolTip(t("Achtergrond / gum (rechtermuisknop)"))
        self.bg_btn.clicked.connect(lambda: self.pick_color(True))
        v.addWidget(self.fg_btn)
        v.addWidget(self.bg_btn)
        self.swap_btn = QPushButton("\u21c4  " + t("Wisselen")); self.swap_btn.setMinimumHeight(32)
        self.swap_btn.clicked.connect(self.swap_colors)
        v.addWidget(self.swap_btn)
        pal = QGridLayout(); pal.setSpacing(4)
        for i, col in enumerate(PALETTE):
            pal.addWidget(SwatchButton(col, self._pick_swatch), i // 6, i % 6)
        palw = QWidget(); palw.setLayout(pal)
        v.addWidget(palw, alignment=Qt.AlignmentFlag.AlignHCenter)
        v.addWidget(QLabel(t("Grootte")))
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(1, 80); self.size_slider.setValue(self.canvas.size)
        self.size_slider.valueChanged.connect(self._size_changed)
        self.size_value = QLabel(str(self.canvas.size))
        rowsz = QHBoxLayout(); rowsz.addWidget(self.size_slider, 1); rowsz.addWidget(self.size_value)
        v.addLayout(rowsz)
        v.addWidget(QLabel(t("Penseel: dekking")))
        self.op_brush = QSlider(Qt.Orientation.Horizontal)
        self.op_brush.setRange(1, 100); self.op_brush.setValue(self.canvas.brush_opacity)
        self.op_brush.valueChanged.connect(lambda val: setattr(self.canvas, "brush_opacity", val))
        v.addWidget(self.op_brush)
        v.addWidget(QLabel(t("Penseel: zachtheid")))
        self.soft_brush = QSlider(Qt.Orientation.Horizontal)
        self.soft_brush.setRange(0, 100); self.soft_brush.setValue(self.canvas.brush_softness)
        self.soft_brush.valueChanged.connect(lambda val: setattr(self.canvas, "brush_softness", val))
        v.addWidget(self.soft_brush)
        self.fill_btn = QPushButton(t("Gevuld")); self.fill_btn.setCheckable(True)
        self.fill_btn.setMinimumHeight(36)
        self.fill_btn.clicked.connect(self._toggle_fill)
        v.addWidget(self.fill_btn)
        self.transp_btn = QPushButton(t("Transp. selectie")); self.transp_btn.setCheckable(True)
        self.transp_btn.setChecked(self.canvas.sel_transparent)
        self.transp_btn.setMinimumHeight(36)
        self.transp_btn.setToolTip(t("Achtergrondkleur wordt doorzichtig bij selecteren"))
        self.transp_btn.clicked.connect(
            lambda: setattr(self.canvas, "sel_transparent", self.transp_btn.isChecked()))
        v.addWidget(self.transp_btn)
        v.addStretch(1)
        self.donate_btn = QPushButton("\u2665  " + t("Donatie"))
        self.donate_btn.setToolTip(DONATE_URL)
        self.donate_btn.clicked.connect(self._donate)
        v.addWidget(self.donate_btn)
        return w

    def _build_layers(self):
        w = QWidget(); w.setFixedWidth(240)
        v = QVBoxLayout(w); v.setContentsMargins(0, 0, 0, 0); v.setSpacing(6)
        lbl = QLabel(t("Lagen")); lbl.setStyleSheet("font-weight:bold;")
        v.addWidget(lbl)
        self.layer_list = QListWidget()
        self.layer_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.layer_list.currentRowChanged.connect(self._layer_selected)
        self.layer_list.itemChanged.connect(self._layer_item_changed)
        self.layer_list.itemDoubleClicked.connect(lambda _i: self._rename_layer())
        v.addWidget(self.layer_list, 1)
        row1 = QHBoxLayout(); row1.setSpacing(6)
        b_add = QPushButton("+"); b_add.setToolTip(t("Nieuwe laag")); b_add.setMinimumHeight(38)
        b_add.clicked.connect(self.add_layer)
        b_del = QPushButton("🗑"); b_del.setToolTip(t("Laag verwijderen")); b_del.setMinimumHeight(38)
        b_del.clicked.connect(self.delete_layer)
        b_up = QPushButton("▲"); b_up.setToolTip(t("Omhoog")); b_up.setMinimumHeight(38)
        b_up.clicked.connect(lambda: self.move_layer(-1))
        b_dn = QPushButton("▼"); b_dn.setToolTip(t("Omlaag")); b_dn.setMinimumHeight(38)
        b_dn.clicked.connect(lambda: self.move_layer(1))
        for b in (b_add, b_del, b_up, b_dn):
            row1.addWidget(b)
        v.addLayout(row1)
        v.addWidget(QLabel(t("Transparantie")))
        self.op_slider = QSlider(Qt.Orientation.Horizontal)
        self.op_slider.setRange(0, 100); self.op_slider.setValue(100)
        self.op_slider.valueChanged.connect(self._opacity_changed)
        v.addWidget(self.op_slider)
        return w

    # -- menu
    def _build_menu(self):
        mb = self.menuBar()
        m_file = mb.addMenu(t("Bestand"))
        self._act(m_file, t("Nieuw"), self.new_canvas, "Ctrl+N")
        self._act(m_file, t("Openen..."), self.open_file, "Ctrl+O")
        self._act(m_file, t("Openen als laag..."), self.open_as_layer)
        m_file.addSeparator()
        self._act(m_file, t("Opslaan project..."), self.save_project, "Ctrl+S")
        self._act(m_file, t("Exporteren..."), self.export_image, "Ctrl+E")
        m_file.addSeparator()
        self._act(m_file, t("Afsluiten"), self.close, "Ctrl+Q")

        m_edit = mb.addMenu(t("Bewerken"))
        self._act(m_edit, t("Ongedaan maken"), self.canvas.undo, "Ctrl+Z")
        self._act(m_edit, t("Opnieuw"), self.canvas.redo, "Ctrl+Y")
        m_edit.addSeparator()
        self._act(m_edit, t("Knippen"), self.canvas.cut_selection, "Ctrl+X")
        self._act(m_edit, t("Kopieren"), self.canvas.copy_selection, "Ctrl+C")
        self._act(m_edit, t("Plakken"), self.canvas.paste, "Ctrl+V")

        m_view = mb.addMenu(t("Beeld"))
        self._act(m_view, t("Inzoomen"), lambda: self.canvas.set_zoom(self.canvas.zoom * 1.25), "+")
        self._act(m_view, t("Uitzoomen"), lambda: self.canvas.set_zoom(self.canvas.zoom / 1.25), "-")
        self._act(m_view, t("Werkelijke grootte"), lambda: self.canvas.set_zoom(1.0), "Ctrl+0")
        self._act(m_view, t("Passend maken"), self.canvas.fit_to_window)

        m_img = mb.addMenu(t("Afbeelding"))
        self._act(m_img, t("Bijsnijden tot selectie"), self.crop_to_selection)
        self._act(m_img, t("Formaat wijzigen..."), self.resize_image)
        self._act(m_img, t("Canvasgrootte..."), self.resize_canvas_dialog)
        m_img.addSeparator()
        self._act(m_img, t("Draaien rechtsom"),
                  lambda: self.canvas.apply_image_op(lambda: self.canvas.project.rotate90(True)))
        self._act(m_img, t("Draaien linksom"),
                  lambda: self.canvas.apply_image_op(lambda: self.canvas.project.rotate90(False)))
        self._act(m_img, t("Spiegelen horizontaal"),
                  lambda: self.canvas.apply_image_op(lambda: self.canvas.project.flip(True)))
        self._act(m_img, t("Spiegelen verticaal"),
                  lambda: self.canvas.apply_image_op(lambda: self.canvas.project.flip(False)))

        m_lang = mb.addMenu(t("Taal"))
        self._act(m_lang, t("Nederlands"), lambda: self.apply_language("nl"))
        self._act(m_lang, t("Engels"), lambda: self.apply_language("en"))

        m_help = mb.addMenu(t("Help"))
        self._act(m_help, t("Snelgids"), self.show_guide, "F1")
        self._act(m_help, t("Over"), self.show_about)

    def _act(self, menu, text, slot, shortcut=None):
        a = QAction(text, self)
        if shortcut:
            a.setShortcut(shortcut)
        a.triggered.connect(slot)
        menu.addAction(a)
        return a

    # -- afbeelding-bewerkingen
    def crop_to_selection(self):
        c = self.canvas
        if c.sel_rect is None:
            QMessageBox.information(self, APP_NAME,
                                    t("Maak eerst een selectie om op bij te snijden."))
            return
        rect = QRect(c.sel_rect)
        c.apply_image_op(lambda: c.project.crop(rect))

    def resize_image(self):
        c = self.canvas
        dlg = ResizeDialog(self, c.project.width, c.project.height, t("Formaat wijzigen"))
        if dlg.exec():
            w, h = dlg.values()
            c.apply_image_op(lambda: c.project.scale_to(w, h))

    def resize_canvas_dialog(self):
        c = self.canvas
        dlg = ResizeDialog(self, c.project.width, c.project.height, t("Canvasgrootte"))
        if dlg.exec():
            w, h = dlg.values()
            c.apply_image_op(lambda: c.project.resize_canvas(w, h))

    # -- tool actions
    def select_tool(self, key):
        if key not in ("select", "lasso"):
            self.canvas.commit_selection()
        if key != "polygon":
            self.canvas._poly_pts = None
            self.canvas._poly_cursor = None
        self.canvas.tool = key
        for k, b in self.tool_buttons.items():
            b.setChecked(k == key)
        self.fill_btn.setEnabled(key in ("rectangle", "ellipse", "roundrect", "polygon"))

    def _size_changed(self, v):
        self.canvas.size = v
        self.size_value.setText(str(v))

    def _toggle_fill(self):
        self.canvas.fill_shapes = self.fill_btn.isChecked()

    def pick_color(self, to_bg=False):
        current = self.canvas.bg if to_bg else self.canvas.fg
        c = QColorDialog.getColor(current, self, t("Kleur 2") if to_bg else t("Kleur 1"))
        if c.isValid():
            if to_bg:
                self.canvas.bg = c
            else:
                self.canvas.fg = c
            self.update_color_buttons()

    def swap_colors(self):
        self.canvas.fg, self.canvas.bg = self.canvas.bg, self.canvas.fg
        self.update_color_buttons()

    def _pick_swatch(self, color, to_bg):
        if to_bg:
            self.canvas.bg = QColor(color)
        else:
            self.canvas.fg = QColor(color)
        self.update_color_buttons()

    def _color_btn_style(self, c):
        tc = "#000000" if (c.red() + c.green() + c.blue()) > 360 else "#ffffff"
        return (f"background:{c.name()}; color:{tc}; border:1px solid {LINE}; "
                f"border-radius:8px; padding:8px 10px; font-size:14px; text-align:left;")

    def update_color_buttons(self):
        self.fg_btn.setStyleSheet(self._color_btn_style(self.canvas.fg))
        self.fg_btn.setText(t("Kleur 1") + "  " + self.canvas.fg.name())
        self.bg_btn.setStyleSheet(self._color_btn_style(self.canvas.bg))
        self.bg_btn.setText(t("Kleur 2") + "  " + self.canvas.bg.name())

    def update_pos_label(self, ip):
        self.pos_label.setText(f"  {ip.x()}, {ip.y()}  ")

    def update_zoom_label(self):
        self.zoom_label.setText(f"{int(self.canvas.zoom * 100)}%")

    def _donate(self):
        try:
            import webbrowser
            webbrowser.open(DONATE_URL)
        except Exception:
            QMessageBox.information(self, t("Donatie"), DONATE_URL)

    # -- layers
    def refresh_layers(self):
        self.layer_list.blockSignals(True)
        self.layer_list.clear()
        for i in range(len(self.project.layers) - 1, -1, -1):
            lay = self.project.layers[i]
            it = QListWidgetItem(lay.name)
            it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEditable)
            it.setCheckState(Qt.CheckState.Checked if lay.visible else Qt.CheckState.Unchecked)
            it.setData(Qt.ItemDataRole.UserRole, i)
            self.layer_list.addItem(it)
        # select active
        for row in range(self.layer_list.count()):
            if self.layer_list.item(row).data(Qt.ItemDataRole.UserRole) == self.project.active:
                self.layer_list.setCurrentRow(row)
                break
        self.layer_list.blockSignals(False)
        lay = self.project.active_layer()
        if lay is not None:
            self.op_slider.blockSignals(True)
            self.op_slider.setValue(lay.opacity)
            self.op_slider.blockSignals(False)

    def _layer_selected(self, row):
        if row < 0:
            return
        it = self.layer_list.item(row)
        if it is None:
            return
        self.project.active = it.data(Qt.ItemDataRole.UserRole)
        lay = self.project.active_layer()
        if lay is not None:
            self.op_slider.blockSignals(True)
            self.op_slider.setValue(lay.opacity)
            self.op_slider.blockSignals(False)

    def _layer_item_changed(self, it):
        idx = it.data(Qt.ItemDataRole.UserRole)
        if idx is None or not (0 <= idx < len(self.project.layers)):
            return
        lay = self.project.layers[idx]
        lay.visible = it.checkState() == Qt.CheckState.Checked
        new_name = it.text().strip()
        if new_name:
            lay.name = new_name
        self.canvas.update()

    def _rename_layer(self):
        lay = self.project.active_layer()
        if lay is None:
            return
        name, ok = QInputDialog.getText(self, t("Naam wijzigen"), t("Laag"), text=lay.name)
        if ok and name.strip():
            lay.name = name.strip()
            self.refresh_layers()

    def add_layer(self):
        lay = Layer(self.project.width, self.project.height,
                    name=f"{t('Laag')} {len(self.project.layers) + 1}")
        self.project.layers.append(lay)
        self.project.active = len(self.project.layers) - 1
        self.canvas.dirty = True
        self.refresh_layers(); self.canvas.update(); self.update_title()

    def delete_layer(self):
        if len(self.project.layers) <= 1:
            return
        del self.project.layers[self.project.active]
        self.project.active = max(0, self.project.active - 1)
        self.canvas.dirty = True
        self.refresh_layers(); self.canvas.update(); self.update_title()

    def move_layer(self, direction):
        i = self.project.active
        j = i + direction
        if 0 <= j < len(self.project.layers):
            self.project.layers[i], self.project.layers[j] = \
                self.project.layers[j], self.project.layers[i]
            self.project.active = j
            self.canvas.dirty = True
            self.refresh_layers(); self.canvas.update(); self.update_title()

    def _opacity_changed(self, v):
        lay = self.project.active_layer()
        if lay is not None:
            lay.opacity = v
            self.canvas.dirty = True
            self.canvas.update()

    # -- files
    def _confirm_discard(self):
        if not self.canvas.dirty:
            return True
        r = QMessageBox.question(
            self, t("Niet opgeslagen wijzigingen"),
            t("Er zijn niet-opgeslagen wijzigingen. Toch doorgaan?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        return r == QMessageBox.StandardButton.Yes

    def new_canvas(self):
        if not self._confirm_discard():
            return
        dlg = NewCanvasDialog(self, self.project.width, self.project.height)
        if dlg.exec():
            w, h, bg = dlg.values()
            self.project = Project(w, h, bg)
            self.path = None
            self.canvas.set_project(self.project)
            self.update_title()

    def _image_filter(self):
        return (t("Afbeeldingen") +
                " (*.png *.jpg *.jpeg *.bmp *.gif *.webp *.tif *.tiff *.ico);;" +
                t("Alle bestanden") + " (*)")

    def open_file(self):
        if not self._confirm_discard():
            return
        path, _ = QFileDialog.getOpenFileName(
            self, t("Openen..."), "",
            t("DravePaint-project") + " (*.dravepaint);;" + self._image_filter(),
            "", QFileDialog.Option.DontUseNativeDialog)
        if not path:
            return
        try:
            if path.lower().endswith(".dravepaint"):
                with open(path, "r", encoding="utf-8") as f:
                    self.project = Project.from_dict(json.load(f))
            else:
                img = QImage(path)
                if img.isNull():
                    raise ValueError("null image")
                img = img.convertToFormat(QImage.Format.Format_ARGB32)
                self.project = Project(img.width(), img.height(), "transparent")
                self.project.layers[0] = Layer(img.width(), img.height(),
                                                name="Achtergrond", image=img)
            self.path = path if path.lower().endswith(".dravepaint") else None
            self.canvas.set_project(self.project)
            self.update_title()
            self.statusBar().showMessage(os.path.basename(path))
        except Exception as e:
            QMessageBox.warning(self, t("Kon bestand niet openen"), str(e))

    def open_as_layer(self):
        path, _ = QFileDialog.getOpenFileName(self, t("Openen als laag..."), "",
                                              self._image_filter(), "",
                                              QFileDialog.Option.DontUseNativeDialog)
        if not path:
            return
        img = QImage(path)
        if img.isNull():
            QMessageBox.warning(self, t("Kon bestand niet openen"), path); return
        img = img.convertToFormat(QImage.Format.Format_ARGB32)
        canvas_img = QImage(self.project.width, self.project.height, QImage.Format.Format_ARGB32)
        canvas_img.fill(QColor(0, 0, 0, 0))
        pp = QPainter(canvas_img); pp.drawImage(0, 0, img); pp.end()
        lay = Layer(self.project.width, self.project.height,
                    name=os.path.basename(path), image=canvas_img)
        self.project.layers.append(lay)
        self.project.active = len(self.project.layers) - 1
        self.canvas.dirty = True
        self.refresh_layers(); self.canvas.update(); self.update_title()

    def save_project(self):
        path, _ = QFileDialog.getSaveFileName(
            self, t("Opslaan project..."), self.path or "tekening.dravepaint",
            t("DravePaint-project") + " (*.dravepaint)", "",
            QFileDialog.Option.DontUseNativeDialog)
        if not path:
            return
        if not path.lower().endswith(".dravepaint"):
            path += ".dravepaint"
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.project.to_dict(), f)
            self.path = path
            self.canvas.dirty = False
            self.update_title()
            self.statusBar().showMessage(t("Opgeslagen"))
        except Exception as e:
            QMessageBox.warning(self, t("Kon niet opslaan"), str(e))

    def export_image(self):
        path, _ = QFileDialog.getSaveFileName(
            self, t("Exporteren..."), "tekening.png",
            "PNG (*.png);;JPEG (*.jpg);;BMP (*.bmp);;GIF (*.gif);;WEBP (*.webp);;TIFF (*.tiff)",
            "", QFileDialog.Option.DontUseNativeDialog)
        if not path:
            return
        comp = self.project.composite()
        ext = os.path.splitext(path)[1].lower().lstrip(".")
        try:
            if ext in ("jpg", "jpeg"):
                # flatten onto white for formats without alpha
                flat = QImage(comp.size(), QImage.Format.Format_RGB32)
                flat.fill(QColor(255, 255, 255))
                pp = QPainter(flat); pp.drawImage(0, 0, comp); pp.end()
                ok = flat.save(path, "JPG")
            else:
                ok = comp.save(path)
            if not ok and HAVE_PIL:
                qimage_to_pil(comp).save(path)
                ok = True
            if not ok:
                raise ValueError("save failed")
            self.statusBar().showMessage(t("Geexporteerd"))
        except Exception as e:
            QMessageBox.warning(self, t("Kon niet opslaan"), str(e))

    # -- misc
    def apply_language(self, code):
        save_lang(code)
        if code == LANG:
            return
        set_lang(code)
        install_qt_translators(code)
        # canvas behouden (incl. project + undo) terwijl we de UI herbouwen
        self.canvas.setParent(None)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(False)
        self.scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(self.canvas)
        left = self._build_tools()
        left_scroll = QScrollArea(); left_scroll.setWidget(left)
        left_scroll.setWidgetResizable(True); left_scroll.setFixedWidth(214)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_scroll.setFrameShape(QFrame.Shape.NoFrame)
        right = self._build_layers()
        central = QWidget(); h = QHBoxLayout(central)
        h.setContentsMargins(8, 8, 8, 8); h.setSpacing(8)
        h.addWidget(left_scroll); h.addWidget(self.scroll, 1); h.addWidget(right)
        self.setCentralWidget(central)
        self.menuBar().clear(); self._build_menu()
        self.select_tool(self.canvas.tool)
        self.update_color_buttons(); self.refresh_layers(); self.update_title()
        self.statusBar().showMessage(t("Klaar"))

    def show_guide(self):
        GuideDialog(self).exec()

    def show_about(self):
        QMessageBox.about(self, t("Over"),
                          f"{APP_NAME} v{APP_VERSION}\nEen {AUTHOR_NAME} product\n{WEBSITE_URL}")

    def update_title(self):
        star = "*" if self.canvas.dirty else ""
        name = os.path.basename(self.path) if self.path else t("Nieuw")
        self.setWindowTitle(f"{star}{name} - {APP_NAME}")

    def update_zoom_label(self):
        self.zoom_label.setText(f"{int(self.canvas.zoom * 100)}%")

    def closeEvent(self, e):
        if self._confirm_discard():
            e.accept()
        else:
            e.ignore()


def _crash_path():
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "dravepaint_fout.txt")


def _install_excepthook():
    def hook(exctype, value, tb):
        import traceback
        msg = "".join(traceback.format_exception(exctype, value, tb))
        try:
            with open(_crash_path(), "w", encoding="utf-8") as f:
                f.write(msg)
        except Exception:
            pass
        try:
            QMessageBox.critical(None, "DravePaint - fout", msg[-1600:])
        except Exception:
            pass
        sys.__excepthook__(exctype, value, tb)
    sys.excepthook = hook


def main():
    _install_excepthook()
    app = QApplication(sys.argv)
    set_lang(load_lang() or "nl")        # Dravenlock-basistaal: Nederlands
    install_qt_translators(LANG)
    app.setApplicationName(APP_NAME)
    app.setWindowIcon(app_icon())
    win = MainWindow()
    win.show()
    win.canvas.fit_to_window()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

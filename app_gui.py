# museum_pyqt.py
import sys
import os
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QTextEdit, QTabWidget, QSpinBox, QFrame
)
from PyQt6.QtGui import QFontDatabase, QFont, QAction, QIcon
from PyQt6.QtCore import Qt
import mysql.connector
from config import DATABASE_CONFIG

# --------------------- Helpers: DB ---------------------
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        return conn
    except mysql.connector.Error as e:
        QMessageBox.critical(None, "DB Error", f"Не удалось подключиться к БД:\n{e}")
        return None

# --------------------- Style: Modern Dark ---------------------
DARK_STYLE = """
/* Backgrounds */
QWidget { background: #0f1115; color: #d7d9de; font-family: "Inter", "Segoe UI", Roboto, Arial; }
QTabWidget::pane { border: 0; }
QTabBar::tab { background: #15171b; border: 1px solid #1f2227; padding: 10px 14px; margin-right: 3px; border-top-left-radius: 6px; border-top-right-radius: 6px; }
QTabBar::tab:selected { background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #1f6feb, stop:1 #1a7ad9); color: white; }
QFrame#header { background: #0b0c0f; border-bottom: 1px solid #1e2228; }

/* Buttons */
QPushButton { background: #1e2328; border: 1px solid #2b3138; padding: 8px 12px; border-radius: 6px; }
QPushButton:hover { background: #26303a; }
QPushButton:pressed { background: #162028; }
QPushButton#primary { background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #2a79ff, stop:1 #1b6df0); color: white; font-weight: 600; }

/* Inputs */
QLineEdit, QComboBox, QTextEdit, QSpinBox {
    background: #0f1316; border: 1px solid #26292d; padding: 6px; border-radius: 6px;
    selection-background-color: #2a79ff; selection-color: white;
}
QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 20px; }

/* Table */
QTableWidget { background: #0f1115; gridline-color: #1d2126; }
QHeaderView::section { background: #0f1115; border-bottom: 1px solid #1d2126; padding: 8px; }
QTableWidget::item:selected { background: #264e9f; color: white; }

/* Labels */
QLabel#title { font-size: 18px; font-weight: 700; color: #ffffff; }

/* Minor tweaks */
QScrollBar:vertical { background: #0f1115; width:12px; }
QScrollBar::handle:vertical { background: #2a2f35; min-height:20px; border-radius:6px; }
"""

# --------------------- Главное окно ---------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MuseumIS — Modern Dark")
        self.resize(1200, 760)

        # Шрифты
        self.load_fonts()

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(64)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(14, 8, 14, 8)
        title = QLabel("Информационная система: Учет экспонатов")
        title.setObjectName("title")
        header_layout.addWidget(title)
        header_layout.addStretch()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark"])
        self.theme_combo.setFixedWidth(110)
        header_layout.addWidget(QLabel("Тема:"))
        header_layout.addWidget(self.theme_combo)
        main_layout.addWidget(header)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.tab_add = QWidget()
        self.tab_move = QWidget()
        self.tab_delete = QWidget()
        self.tab_view = QWidget()
        self.tab_analytics = QWidget()

        self.tabs.addTab(self.tab_add, "Добавить")
        self.tabs.addTab(self.tab_move, "Переместить")
        self.tabs.addTab(self.tab_delete, "Удалить")
        self.tabs.addTab(self.tab_view, "Текущий статус")
        self.tabs.addTab(self.tab_analytics, "Аналитика")

        self.build_add_tab()
        self.build_move_tab()
        self.build_delete_tab()
        self.build_view_tab()
        self.build_analytics_tab()

        self.status = self.statusBar()
        self.status.showMessage("Готово")

        self.setStyleSheet(DARK_STYLE)

        self.load_report_view()
        self.load_analytics()

    def load_fonts(self):
        font_folder = os.path.join(os.path.dirname(__file__), "fonts")
        if os.path.isdir(font_folder):
            for fname in os.listdir(font_folder):
                if fname.lower().endswith((".ttf", ".otf")):
                    QFontDatabase.addApplicationFont(os.path.join(font_folder, fname))
        app_font = QFont("Inter", 10)
        QApplication.instance().setFont(app_font)

    def build_add_tab(self):
        layout = QHBoxLayout(self.tab_add)
        left = QVBoxLayout()
        left.setSpacing(8)
        left.setContentsMargins(12, 12, 12, 12)

        lbl = QLabel("Добавление нового экспоната")
        lbl.setStyleSheet("font-weight:700; font-size:14px;")
        left.addWidget(lbl)

        self.input_title = QLineEdit()
        self.input_title.setPlaceholderText("Название")
        left.addWidget(self.input_title)

        self.input_acc = QLineEdit()
        self.input_acc.setPlaceholderText("Инв. №")
        left.addWidget(self.input_acc)

        self.input_year = QSpinBox()
        self.input_year.setRange(1000, 2100)
        self.input_year.setValue(2000)
        self.input_year.setPrefix("Год: ")
        left.addWidget(self.input_year)

        self.input_value = QLineEdit()
        self.input_value.setPlaceholderText("Стоимость (USD)")
        left.addWidget(self.input_value)

        self.input_condition = QComboBox()
        self.input_condition.addItems(["Excellent", "Good", "Fair", "Poor"])
        left.addWidget(self.input_condition)

        self.input_author = QLineEdit()
        self.input_author.setPlaceholderText("ID Автора")
        left.addWidget(self.input_author)

        self.input_collection = QLineEdit()
        self.input_collection.setPlaceholderText("ID Коллекции")
        left.addWidget(self.input_collection)

        btn_add = QPushButton("Добавить в базу")
        btn_add.setObjectName("primary")
        btn_add.clicked.connect(self.action_add_exhibit)
        btn_add.setFixedHeight(36)
        left.addWidget(btn_add)

        left.addStretch()
        layout.addLayout(left, 0)

        right = QVBoxLayout()
        right.setContentsMargins(12, 12, 12, 12)
        right.addWidget(QLabel("Инструменты"))
        note = QLabel("После добавления запись появится в 'Текущий статус'.")
        note.setWordWrap(True)
        right.addWidget(note)
        right.addStretch()
        layout.addLayout(right, 1)

    def action_add_exhibit(self):
        title = self.input_title.text().strip()
        acc = self.input_acc.text().strip()
        year = self.input_year.value()
        val = self.input_value.text().strip()
        cond = self.input_condition.currentText()
        try:
            author_id = int(self.input_author.text().strip())
            coll_id = int(self.input_collection.text().strip())
        except:
            QMessageBox.warning(self, "Ошибка ввода", "ID Автора и ID Коллекции должны быть числами.")
            return

        if not (title and acc and val):
            QMessageBox.warning(self, "Ошибка ввода", "Название, Инв. № и Стоимость обязательны.")
            return

        try:
            val_float = float(val)
        except:
            QMessageBox.warning(self, "Ошибка ввода", "Стоимость должна быть числом.")
            return

        conn = get_db_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            sql = """
            INSERT INTO Exhibits (title, accession_number, date_created, value, condition_rating, author_id, collection_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (title, acc, year, val_float, cond, author_id, coll_id))
            conn.commit()
            QMessageBox.information(self, "Готово", f"Экспонат '{title}' добавлен.")
            self.input_title.clear(); self.input_acc.clear(); self.input_value.clear()
            self.input_author.clear(); self.input_collection.clear()
            self.load_report_view()
            self.load_analytics()
        except mysql.connector.Error as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка БД", str(e))
        finally:
            cursor.close()
            conn.close()

    def build_move_tab(self):
        layout = QVBoxLayout(self.tab_move)
        layout.setContentsMargins(12, 12, 12, 12)

        lbl = QLabel("Перемещение экспоната (хранимая процедура)")
        lbl.setStyleSheet("font-weight:700; font-size:14px;")
        layout.addWidget(lbl)

        self.move_exhibit_id = QLineEdit()
        self.move_exhibit_id.setPlaceholderText("ID экспоната")
        layout.addWidget(self.move_exhibit_id)

        self.move_location_id = QLineEdit()
        self.move_location_id.setPlaceholderText("Новый ID зала")
        layout.addWidget(self.move_location_id)

        self.move_note = QLineEdit()
        self.move_note.setPlaceholderText("Примечание")
        layout.addWidget(self.move_note)

        btn_move = QPushButton("Переместить")
        btn_move.clicked.connect(self.action_move_exhibit)
        layout.addWidget(btn_move)
        layout.addStretch()

    def action_move_exhibit(self):
        try:
            ex_id = int(self.move_exhibit_id.text().strip())
            loc_id = int(self.move_location_id.text().strip())
        except:
            QMessageBox.warning(self, "Ошибка ввода", "ID должны быть числами.")
            return
        note = self.move_note.text().strip()

        conn = get_db_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.callproc("Move_Exhibit", (ex_id, loc_id, note))
            msg = "Операция выполнена."
            for res in cursor.stored_results():
                row = res.fetchone()
                if row:
                    msg = row[0]
            conn.commit()
            QMessageBox.information(self, "Результат", msg)
            self.load_report_view()
        except mysql.connector.Error as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка БД", str(e))
        finally:
            cursor.close()
            conn.close()

    def build_delete_tab(self):
        layout = QVBoxLayout(self.tab_delete)
        layout.setContentsMargins(12, 12, 12, 12)

        lbl = QLabel("Удаление экспоната (необратимо)")
        lbl.setStyleSheet("font-weight:700; font-size:14px; color:#ff9f9f;")
        layout.addWidget(lbl)

        self.delete_id = QLineEdit()
        self.delete_id.setPlaceholderText("ID экспоната")
        layout.addWidget(self.delete_id)

        btn_del = QPushButton("Удалить навсегда")
        btn_del.setStyleSheet("background: #7c1f1f; color: white;")
        btn_del.clicked.connect(self.action_delete_exhibit)
        layout.addWidget(btn_del)
        layout.addStretch()

    def action_delete_exhibit(self):
        try:
            ex_id = int(self.delete_id.text().strip())
        except:
            QMessageBox.warning(self, "Ошибка ввода", "ID должен быть числом.")
            return
        if QMessageBox.question(self, "Подтверждение", f"Точно удалить экспонат {ex_id}?") != QMessageBox.StandardButton.Yes:
            return

        conn = get_db_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM MovementLog WHERE exhibit_id = %s", (ex_id,))
            cursor.execute("DELETE FROM Exhibits WHERE exhibit_id = %s", (ex_id,))
            if cursor.rowcount == 0:
                conn.rollback()
                QMessageBox.information(self, "Не найден", "Экспонат не найден.")
            else:
                conn.commit()
                QMessageBox.information(self, "Успех", "Экспонат удалён.")
                self.delete_id.clear()
                self.load_report_view()
                self.load_analytics()
        except mysql.connector.Error as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка БД", str(e))
        finally:
            cursor.close()
            conn.close()

    def build_view_tab(self):
        layout = QVBoxLayout(self.tab_view)
        layout.setContentsMargins(12, 12, 12, 12)

        header = QHBoxLayout()
        header.addWidget(QLabel("Текущий статус экспонатов"))
        header.addStretch()
        btn_refresh = QPushButton("Обновить")
        btn_refresh.clicked.connect(self.load_report_view)
        header.addWidget(btn_refresh)
        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Название", "Автор", "Зал", "Состояние"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

    def load_report_view(self):
        self.table.setRowCount(0)
        conn = get_db_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT Exhibit_Title, Author, Current_Location, Condition_Status FROM Current_Exhibit_Status LIMIT 1000")
            rows = cursor.fetchall()
            self.table.setRowCount(len(rows))
            for r, row in enumerate(rows):
                for c, val in enumerate(row):
                    item = QTableWidgetItem(str(val))
                    item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                    self.table.setItem(r, c, item)
            self.status.showMessage(f"Загружено {len(rows)} записей")
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Ошибка БД", str(e))
        finally:
            cursor.close()
            conn.close()

    def build_analytics_tab(self):
        layout = QVBoxLayout(self.tab_analytics)
        layout.setContentsMargins(12, 12, 12, 12)

        lbl = QLabel("Аналитика: Средняя стоимость по коллекциям")
        lbl.setStyleSheet("font-weight:700; font-size:14px;")
        layout.addWidget(lbl)

        self.anal_table = QTableWidget()
        self.anal_table.setColumnCount(3)
        self.anal_table.setHorizontalHeaderLabels(["Коллекция", "Кол-во", "Средняя стоимость USD"])
        self.anal_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.anal_table)

        btn_load = QPushButton("Загрузить")
        btn_load.clicked.connect(self.load_analytics)
        layout.addWidget(btn_load)

    def load_analytics(self):
        self.anal_table.setRowCount(0)
        conn = get_db_connection()
        if not conn:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT C.name, COUNT(E.exhibit_id) AS cnt, ROUND(AVG(E.value),2) AS avgv
                FROM Collections C
                JOIN Exhibits E ON C.collection_id = E.collection_id
                GROUP BY C.name
                HAVING COUNT(E.exhibit_id) > 0
                ORDER BY avgv DESC
                LIMIT 200
            """)
            rows = cursor.fetchall()
            self.anal_table.setRowCount(len(rows))
            for r, row in enumerate(rows):
                self.anal_table.setItem(r, 0, QTableWidgetItem(str(row[0])))
                self.anal_table.setItem(r, 1, QTableWidgetItem(str(row[1])))
                self.anal_table.setItem(r, 2, QTableWidgetItem(f"${row[2]:,.2f}"))
            self.status.showMessage(f"Аналитика: {len(rows)} строк")
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Ошибка БД", str(e))
        finally:
            cursor.close()
            conn.close()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("MuseumIS")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

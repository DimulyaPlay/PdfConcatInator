import traceback
from PySide2.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QDialog, QFileDialog, QCheckBox, QSizePolicy, QStyleFactory
from PySide2.QtGui import QIcon, QCursor, QFont
from PySide2.QtCore import Qt, QSize, QTranslator, QLocale, QLibraryInfo
from custom_file_dialog import CustomFileDialog, resource_path
import pythoncom
import win32com.client as win32
import os
import sys
from functools import partial
import psutil
import shutil
import tempfile
from pdfmerger import merge_two_pages_into_one, merge_four_pages_into_one, merge_pdfs, normalize_pdf_in_place
#  pyinstaller.exe --onefile --windowed --noconfirm --icon "C:\Users\CourtUser\Documents\PyCharmProjects\WordSaveToPDF\icon.ico" --add-data "C:\Users\CourtUser\Documents\PyCharmProjects\WordSaveToPDF\icon.ico;." --add-data "C:\Users\CourtUser\Documents\PyCharmProjects\WordSaveToPDF\assets;assets"  C:\Users\CourtUser\Documents\PyCharmProjects\WordSaveToPDF\PdfConcatInator.py


class FileActionDialog(QDialog):
    def __init__(self, word_files, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup)  # Стиль окна как у контекстного меню
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(4, 4, 4, 4)
        self.setMinimumWidth(300)

        # Словарь для хранения файлов и их чекбоксов
        self.file_checkboxes = {}
        self.layout().addWidget(QLabel('Откройте документ в word чтобы он появился в списке'))
        # Для каждого файла создаем горизонтальный контейнер с чекбоксом и меткой
        if not word_files:
            self.layout().addWidget(QLabel('-Открытых файлов в word не найдено-'))
        for file_path in word_files:
            file_layout = QHBoxLayout()

            # Чекбокс
            checkbox = QCheckBox()
            file_layout.addWidget(checkbox)
            self.file_checkboxes[file_path] = checkbox

            # Имя файла (метка, нажатие по которой также выбирает чекбокс)
            file_label = QLabel(os.path.basename(file_path))
            file_label.setFont(QFont('Arial', 11))
            file_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            file_label.mousePressEvent = partial(self.toggle_checkbox, checkbox)
            file_layout.addWidget(file_label)

            # Добавляем строку в общий лейаут
            self.layout().addLayout(file_layout)

        # Контейнер для кнопок
        button_layout = QHBoxLayout()


        # Кнопка "Объединить в PDF"
        merge_pdf_btn = QPushButton('Объединить pdf')
        merge_pdf_btn.clicked.connect(self.merge_selected_pdfs)
        merge_pdf_btn.setIcon(QIcon(resource_path('assets/pdf_plus.png')))
        merge_pdf_btn.setIconSize(QSize(28, 28))
        merge_pdf_btn.setToolTip('Объединить word с pdf')
        button_layout.addWidget(merge_pdf_btn)

        # Кнопка "Сохранить как PDF"
        save_pdf_btn = QPushButton('Сохранить word в pdf')
        save_pdf_btn.clicked.connect(self.save_selected_as_pdf)
        save_pdf_btn.setEnabled(bool(word_files))
        save_pdf_btn.setIcon(QIcon(resource_path('assets/pdf.png')))
        save_pdf_btn.setIconSize(QSize(28, 28))
        save_pdf_btn.setToolTip('Сохранить word в pdf')
        button_layout.addWidget(save_pdf_btn)

        # Кнопка "Сохранить как Word"
        save_word_btn = QPushButton('Сохранить word в папку')
        save_word_btn.clicked.connect(self.save_selected_as_word)
        save_word_btn.setEnabled(bool(word_files))
        save_word_btn.setIcon(QIcon(resource_path('assets/word.png')))
        save_word_btn.setIconSize(QSize(28, 28))
        save_word_btn.setToolTip('Сохранить word в папку')
        button_layout.addWidget(save_word_btn)

        # Добавляем кнопки в нижнюю часть окна
        self.layout().addLayout(button_layout)

    def toggle_checkbox(self, checkbox, event):
        """Функция для переключения состояния чекбокса при клике на имя файла"""
        checkbox.setChecked(not checkbox.isChecked())

    def save_selected_as_word(self):
        """Сохранение выбранных файлов в формате Word"""
        selected_files = [file for file, checkbox in self.file_checkboxes.items() if checkbox.isChecked()]
        if selected_files:
            self.save_as_word(selected_files)

    def save_selected_as_pdf(self):
        """Сохранение выбранных файлов в формате PDF"""
        selected_files = [file for file, checkbox in self.file_checkboxes.items() if checkbox.isChecked()]
        if selected_files:
            self.save_as_pdf(selected_files)

    def merge_selected_pdfs(self):
        """Объединение выбранных файлов в один PDF"""
        selected_files = [file for file, checkbox in self.file_checkboxes.items() if checkbox.isChecked()]
        if selected_files:
            self.merge_with_another_pdf(selected_files)
        else:
            self.merge_with_another_pdf(None)

    def save_as_word(self, file_paths):
        tempdir = tempfile.mkdtemp()
        for file_path in file_paths:
            default_name = os.path.basename(file_path)
            save_path, _ = QFileDialog.getSaveFileName(self, "Сохранить документ как.", default_name,
                                                       "Word Files (*.docx)")
            if not save_path:
                return
            print(f"Сохранение {file_path} в Word")
            try:
                temp_file = os.path.join(tempdir, os.path.basename(save_path))
                pythoncom.CoInitialize()
                word_app = win32.Dispatch("Word.Application")
                doc = word_app.Documents.Open(file_path)
                doc.SaveAs(temp_file, FileFormat=16)  # 16 - формат DOCX
                print(f"Документ сохранен как {save_path}")
                shutil.copy(temp_file, save_path)
                shutil.rmtree(tempdir)
            except Exception as e:
                traceback.print_exc()

    def save_as_pdf(self, file_paths, dir=None):
        saved_paths = []
        tempdir = tempfile.mkdtemp()
        if dir:
            save_dir = dir
        for file_path in file_paths:
            default_name = os.path.basename(file_path)
            default_name_new = os.path.splitext(default_name)[0]+'.pdf'
            if not dir:
                save_path, _ = QFileDialog.getSaveFileName(self, "Сохранить документ как.", default_name_new,
                                                           "PDF Files (*.pdf)")
            else:
                save_path = os.path.join(save_dir, default_name_new)
                saved_paths.append(save_path)
            if not save_path:
                return

            print(f"Сохранение {file_path} в PDF")
            try:
                temp_file = os.path.join(tempdir, os.path.basename(save_path))
                pythoncom.CoInitialize()
                word_app = win32.Dispatch("Word.Application")
                doc = word_app.Documents.Open(file_path)
                doc.SaveAs(temp_file, FileFormat=17)  # 17 - формат PDF
                print(f"Документ сохранен как {save_path}")
                shutil.copy(temp_file, save_path)
                shutil.rmtree(tempdir)
            except Exception as e:
                traceback.print_exc()
        return saved_paths

    def merge_with_another_pdf(self, file_paths):
        tempdir = tempfile.mkdtemp()
        if file_paths:
            saved_pdf_paths = self.save_as_pdf(file_paths, dir=tempdir)
        else:
            saved_pdf_paths = []
        dialog = CustomFileDialog(saved_pdf_paths)
        if dialog.exec_():
            file_order_and_layouts = dialog.get_file_order_and_layouts()
            save_path, _ = QFileDialog.getSaveFileName(self, "Сохранить документ как.", '',
                                                       "PDF Files (*.pdf)")
            if not save_path:
                return
            list_for_concat = []
            print(f"Объединение {file_order_and_layouts}")
            for fp, lo in file_order_and_layouts:
                new_fp = self.make_layout(fp, lo, tempdir)
                list_for_concat.append(new_fp)
            if list_for_concat:
                merge_pdfs(save_path, list_for_concat, tempdir)
                if dialog.normalize_checkbox.isChecked():
                    normalize_pdf_in_place(save_path)
        shutil.rmtree(tempdir)

    def make_layout(self, filepath, layout, tempdir):
        if layout == 1:
            return filepath
        if layout == 2:
            return merge_two_pages_into_one(filepath, tempdir)
        else:
            return merge_four_pages_into_one(filepath, tempdir)


class WordTrayApp(QSystemTrayIcon, QWidget):
    def __init__(self, icon, parent=None):
        super().__init__(icon, parent)
        self.menu = QMenu()
        self.create_context_menu()
        self.activated.connect(self.on_tray_icon_activated)
        self.show()

    def create_context_menu(self):
        """Создание контекстного меню для ПКМ"""
        exit_action = QAction("Выход", self.menu)
        exit_action.triggered.connect(self.exit_app)
        self.menu.addAction(exit_action)

    def on_tray_icon_activated(self, reason):
        """Обработка нажатий на иконку трея"""
        if reason == QSystemTrayIcon.Trigger:  # ЛКМ
            self.show_documents_widget()
        elif reason == QSystemTrayIcon.Context:  # ПКМ
            self.menu.exec_(QCursor.pos())

    def show_documents_widget(self):
        """Показ виджета с документами и действиями при нажатии ЛКМ"""
        cursor_pos = QCursor.pos()
        word_files = self.get_open_word_files()
        dialog = FileActionDialog(word_files, self)
        dialog.adjustSize()
        dialog_width = dialog.width()
        dialog_height = dialog.height()
        new_x = cursor_pos.x() - dialog_width
        new_y = cursor_pos.y() - dialog_height
        dialog.move(new_x, new_y)
        dialog.exec_()

    def get_open_word_files(self):
        """Получение списка открытых файлов Word через psutil"""
        word_files = []
        # Поиск процессов winword.exe
        word_processes = [p.info for p in psutil.process_iter(attrs=['pid', 'name']) if 'WINWORD.EXE' in p.info['name'].upper()]

        if word_processes:
            # Берем PID первого найденного процесса
            pid = word_processes[0]['pid']
            p = psutil.Process(pid)

            # Получаем список открытых файлов для процесса winword.exe
            open_files = p.open_files()

            # Фильтрация файлов по расширениям .doc и .docx
            word_files = [f.path for f in open_files if f.path.lower().endswith(('.doc', '.docx'))]

        return word_files

    def exit_app(self):
        self.hide()
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    translator = QTranslator()
    locale = QLocale.system().name()  # Получение системной локали
    path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)  # Путь к переводам Qt
    translator.load("qtbase_" + locale, path)
    app.installTranslator(translator)
    app.setStyle(QStyleFactory.create("Fusion"))
    tray_app = WordTrayApp(QIcon(resource_path("icon.ico")))
    sys.exit(app.exec_())

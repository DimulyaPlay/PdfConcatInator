import os
from PySide2.QtWidgets import (QDialog, QVBoxLayout, QLabel, QPushButton, QRadioButton, QListWidget,
                               QListWidgetItem, QWidget, QHBoxLayout, QApplication, QAbstractItemView)
from PySide2.QtGui import QIcon, QPixmap, QDragEnterEvent, QDropEvent, QCursor
from PySide2.QtCore import QSize, Qt


class CustomFileDialog(QDialog):
    def __init__(self, file_paths):
        super().__init__()
        self.setMinimumWidth(400)
        self.setWindowTitle("PDF+")
        self.setWindowIcon(QIcon('icon.ico'))
        self.file_paths = file_paths  # Список переданных файлов
        self.setAcceptDrops(True)
        # Основной макет диалога
        layout = QVBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)

        # Инструкция
        label = QLabel()
        instr = '  1. Для добавления файлов перетаскивайте их В это окно. \n  2. Чтобы удалить, нажмите правой кнопкой мыши.\n  2. Чтобы задать порядок перемещайте файлы между собой. \n  3. Укажите макет ' \
                'расположения для файлов и нажмите объединить.'

        label.setText(instr)
        label.setWordWrap(True)
        layout.addWidget(label)

        # Список файлов с возможностью перетаскивания
        self.file_list_widget = QListWidget(self)
        self.file_list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.file_list_widget.setAcceptDrops(True)  # Разрешаем принимать перетаскиваемые элементы
        self.file_list_widget.setDropIndicatorShown(True)  # Показ индикатора при перетаскивании
        self.file_list_widget.setDragDropMode(QAbstractItemView.InternalMove)  # Включаем перетаскивание
        self.file_list_widget.dragMoveEvent = self.dragMoveEvent_custom
        layout.addWidget(self.file_list_widget)

        # Добавляем элементы в список
        for file_path in file_paths:
            self.add_file_item(file_path)

        # Кнопка подтверждения
        self.confirm_button = QPushButton("Объединить")
        self.confirm_button.clicked.connect(self.accept)
        layout.addWidget(self.confirm_button)

    def add_file_item(self, file_path):
        """Добавляем файл как элемент списка"""
        if self.is_file_in_list(file_path):
            return  # Если файл уже есть в списке, не добавляем его
        file_item = QListWidgetItem(self.file_list_widget)
        file_widget = QWidget()

        # Горизонтальный макет для виджета файла
        file_layout = QHBoxLayout(file_widget)
        file_layout.setContentsMargins(3, 3, 3, 3)

        # Имя файла
        file_label = QLabel(os.path.basename(file_path))
        file_label.setToolTip(file_path)  # Показываем полный путь при наведении
        file_label.mouseDoubleClickEvent = lambda e, filepath = file_path: os.startfile(filepath)
        file_layout.addWidget(file_label, stretch=1)
        # Обработка события правой кнопки мыши для удаления
        def remove_item(event):
            if event.button() == Qt.RightButton:
                row = self.file_list_widget.row(file_item)
                self.file_list_widget.takeItem(row)
            else:
                event.ignore()
        file_label.mousePressEvent = remove_item

        # Радиокнопки для выбора макета (1 на 1, 2 на 1, 4 на 1)
        self.add_layout_radio_buttons(file_layout)

        # Привязываем виджет к элементу списка
        file_item.setSizeHint(file_widget.sizeHint())
        self.file_list_widget.setItemWidget(file_item, file_widget)
        # Перерасчет ширины окна на основе самого широкого элемента
        self.update_window_width()

    def add_layout_radio_buttons(self, layout):
        """Добавляем радиокнопки с иконками макетов в указанный лейаут"""
        iconsizex, iconsizey = 26, 26
        layout_1x1_radio = QRadioButton()
        layout_1x1_radio.setIcon(QIcon(QPixmap('assets/1.png')))
        layout_1x1_radio.setIconSize(QSize(iconsizex, iconsizey))
        layout_1x1_radio.setChecked(True)  # Установим по умолчанию 1 на 1
        layout.addWidget(layout_1x1_radio)

        layout_2x1_radio = QRadioButton()
        layout_2x1_radio.setIcon(QIcon(QPixmap('assets/2.png')))
        layout_2x1_radio.setIconSize(QSize(iconsizex, iconsizey))
        layout.addWidget(layout_2x1_radio)

        layout_4x1_radio = QRadioButton()
        layout_4x1_radio.setIcon(QIcon(QPixmap('assets/4.png')))
        layout_4x1_radio.setIconSize(QSize(iconsizex, iconsizey))
        layout.addWidget(layout_4x1_radio)

    def update_window_width(self):
        """Обновляем ширину окна в зависимости от самого широкого элемента"""
        max_width = 0
        for index in range(self.file_list_widget.count()):
            item_widget = self.file_list_widget.itemWidget(self.file_list_widget.item(index))
            if item_widget:
                item_width = item_widget.sizeHint().width()
                max_width = max(max_width, item_width)
        max_width += 20
        self.setMinimumWidth(max(self.minimumWidth(), max_width))

    def get_file_order_and_layouts(self):
        """Получаем текущий порядок файлов и их макеты"""
        file_order_and_layouts = []
        for index in range(self.file_list_widget.count()):
            item_widget = self.file_list_widget.itemWidget(self.file_list_widget.item(index))
            file_label = item_widget.findChild(QLabel)
            file_name = file_label.toolTip()

            # Определяем выбранный макет
            layout_radios = item_widget.findChildren(QRadioButton)
            layout = 1 if layout_radios[0].isChecked() else 2 if layout_radios[1].isChecked() else 4

            file_order_and_layouts.append((file_name, layout))

        return file_order_and_layouts

    def is_file_in_list(self, file_path):
        """Проверяем, есть ли файл в списке (по полному пути)"""
        for index in range(self.file_list_widget.count()):
            item_widget = self.file_list_widget.itemWidget(self.file_list_widget.item(index))
            file_label = item_widget.findChild(QLabel)
            if file_label and file_label.toolTip() == file_path:  # Сравниваем полный путь (в toolTip)
                return True
        return False

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Обработка события перетаскивания файлов извне"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Добавление файла в список при перетаскивании PDF файлов извне"""
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith('.pdf'):
                self.add_file_item(file_path)
        event.acceptProposedAction()

    def dragMoveEvent_custom(self, event):
        if ((target := self.file_list_widget.row(self.file_list_widget.itemAt(event.pos()))) ==
                (current := self.file_list_widget.currentRow()) + 1 or
                (current == self.file_list_widget.count() - 1 and target == -1)):
            event.ignore()
        else:
            event.accept()

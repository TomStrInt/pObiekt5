import sys
from PySide6.QtCore import QAbstractTableModel, Qt, QDate
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTableView,
    QVBoxLayout, QPushButton, QWidget, QMessageBox
)
from PySide6.QtGui import QBrush, QColor


class BookModel(QAbstractTableModel):
    def __init__(self, books=None):
        super().__init__()
        self.books = books or []

    def rowCount(self, parent=None):
        return len(self.books)

    def columnCount(self, parent=None):
        return 5  

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        book = self.books[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0:
                return book["title"]
            elif col == 1:
                return book["author"]
            elif col == 2:
                return book["genre"]
            elif col == 3:
                return "Dostępna" if book["status"] == "available" else "Wypożyczona"
            elif col == 4:
                return book["borrow_date"].toString("yyyy-MM-dd") if book["borrow_date"] else ""

        if role == Qt.DecorationRole and col == 3:
            return QColor("green") if book["status"] == "available" else QColor("red")

        if role == Qt.BackgroundRole and col == 3:
            if book["status"] == "borrowed" and book["borrow_date"]:
                overdue = book["borrow_date"].addDays(14)
                if QDate.currentDate() > overdue:
                    return QBrush(QColor("red"))

        return None

    def sort(self, column, order=Qt.AscendingOrder):
        reverse = order == Qt.DescendingOrder
        if column == 0:
            key = lambda b: b["title"]
        elif column == 1:
            key = lambda b: b["author"]
        elif column == 4:
            key = lambda b: b["borrow_date"] or QDate()
        else:
            return

        self.layoutAboutToBeChanged.emit()
        self.books.sort(key=key, reverse=reverse)
        self.layoutChanged.emit()


class LibraryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Biblioteka")

        self.model = BookModel([
            {"title": "Wiedźmin", "author": "Andrzej Sapkowski", "genre": "Fantasy",
             "status": "borrowed", "borrow_date": QDate.currentDate().addDays(-16)},
            {"title": "Harry Potter", "author": "J.K. Rowling", "genre": "Fantasy",
             "status": "available", "borrow_date": None},
            {"title": "Lalka", "author": "Bolesław Prus", "genre": "Klasyka",
             "status": "borrowed", "borrow_date": QDate.currentDate().addDays(-10)},
            {"title": "Kapitał", "author": "Karol Marks", "genre": "Ekonomia, Polityka",
             "status": "borrowed", "borrow_date": QDate.currentDate().addDays(-7)}
        ])

        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setSortingEnabled(True)

        btn = QPushButton("Sprawdź przedawnione")
        btn.clicked.connect(self.check_overdue_books)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def check_overdue_books(self):
        overdue = [
            b["title"]
            for b in self.model.books
            if b["status"] == "borrowed"
            and b["borrow_date"]
            and QDate.currentDate() > b["borrow_date"].addDays(14)
        ]
        if overdue:
            QMessageBox.warning(
                self,
                "Przedawnione książki",
                "Przedawnione książki:\n" + ", ".join(overdue)
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = LibraryApp()
    win.show()
    sys.exit(app.exec())

import sys
from PyQt5.QtCore import QAbstractTableModel, Qt, QVariant, QDate
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QVBoxLayout, QPushButton, QWidget, QMessageBox
from PyQt5.QtGui import QBrush, QColor


class BookModel(QAbstractTableModel):
    def __init__(self, books=None):
        super().__init__()
        self.books = books or []

    def rowCount(self, parent=None):
        return len(self.books)

    def columnCount(self, parent=None):
        return 5  # Tytuł, Autor, Gatunek, Status, Data wypożyczenia

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        book = self.books[index.row()]
        column = index.column()

        if role == Qt.DisplayRole:
            if column == 0:
                return book["title"]
            elif column == 1:
                return book["author"]
            elif column == 2:
                return book["genre"]
            elif column == 3:
                return "Dostępna" if book["status"] == "available" else "Wypożyczona"
            elif column == 4:
                return book["borrow_date"].toString("yyyy-MM-dd") if book["borrow_date"] else ""

        if role == Qt.DecorationRole and column == 3:
            return QColor("green") if book["status"] == "available" else QColor("red")

        if role == Qt.BackgroundRole and column == 3:
            if book["status"] == "borrowed" and book["borrow_date"]:
                overdue_date = book["borrow_date"].addDays(14)
                if QDate.currentDate() > overdue_date:
                    return QBrush(QColor("red"))

        return QVariant()

    def sort(self, column, order):
        if column == 0:  # Sortowanie po tytule
            self.books.sort(key=lambda x: x["title"], reverse=order == Qt.DescendingOrder)
        elif column == 1:  # Sortowanie po autorze
            self.books.sort(key=lambda x: x["author"], reverse=order == Qt.DescendingOrder)
        elif column == 4:  # Sortowanie po dacie wypożyczenia
            self.books.sort(key=lambda x: x["borrow_date"] or QDate(), reverse=order == Qt.DescendingOrder)
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
        ])

        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setSortingEnabled(True)

        self.check_overdue_books()

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        button = QPushButton("Sprawdź przedawnione")
        button.clicked.connect(self.check_overdue_books)
        layout.addWidget(button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def check_overdue_books(self):
        overdue_books = [
            book["title"]
            for book in self.model.books
            if book["status"] == "borrowed" and book["borrow_date"] and
            QDate.currentDate() > book["borrow_date"].addDays(14)
        ]

        if overdue_books:
            QMessageBox.warning(self, "Przedawnione książki", f"Przedawnione książki:\n{', '.join(overdue_books)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LibraryApp()
    window.show()
    sys.exit(app.exec_())

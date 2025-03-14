from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
)


class MarkedPersonsWidget(QWidget):
    def __init__(self, parent=None, max_width=300):
        super().__init__(parent)

        self.remove_all_button = None
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        self.setFixedWidth(max_width)

        # Initialize the dictionary to store marked persons
        self.marked_persons = {}

    def add_person(self, person):
        """
        Add a person to the list and display in the UI.
        :param person: A Person object with a `name` attribute.
        """

        if not self.marked_persons:
            # Create and add the "Remove All" button
            self.remove_all_button = QPushButton("Remove All")
            self.remove_all_button.clicked.connect(self._remove_all)
            self.layout.addWidget(self.remove_all_button)

        self.marked_persons[person.name] = person

        person_layout = QHBoxLayout()

        name_label = QLabel(person.name)
        person_layout.addWidget(name_label)

        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        person_layout.addSpacerItem(spacer)

        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(lambda: self.remove_person(person.name))
        person_layout.addWidget(remove_button)

        self.layout.addLayout(person_layout)

    def remove_person(self, name):
        """
        Remove a person from the list and the UI based on their name.
        :param name: The name of the person to remove.
        """
        # Remove from dictionary
        self.marked_persons.pop(name, None)

        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            if not isinstance(item, QHBoxLayout):
                continue

            # Check if the first widget in the layout is a QLabel with the matching name
            if not (isinstance(item.itemAt(0).widget(), QLabel) and item.itemAt(0).widget().text() == name):
                continue

            # Remove all widgets in the layout and layout itself
            while item.count():
                widget_item = item.takeAt(0)
                widget = widget_item.widget()
                if widget:
                    widget.deleteLater()
            self.layout.removeItem(item)
            break

        if not self.marked_persons and self.remove_all_button:
            self.remove_all_button.deleteLater()

    def _remove_all(self):
        """
        Remove all persons from the list and the UI.
        """
        # Clear the dictionary of marked persons
        self.marked_persons.clear()

        # Remove all layouts and widgets from the list
        for i in range(self.layout.count()):
            item = self.layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()

    def __contains__(self, item):
        return item in self.marked_persons

    def update_person(self, person):
        if person.name in self.marked_persons:
            self.marked_persons[person.name] = person
        else:
            self.add_person(person)

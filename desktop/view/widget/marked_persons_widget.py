from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
)


class MarkedPersonsWidget(QWidget):
    def __init__(self, parent=None, max_width=300):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        self.setFixedWidth(max_width)

        self.marked_persons = {}

    def add_person(self, person):
        """
        Add a person to the list and display in the UI.
        :param person: A Person object with a `name` attribute.
        """
        self.marked_persons[person.name] = person

        person_layout = QHBoxLayout()

        name_label = QLabel(person.name)
        person_layout.addWidget(name_label)

        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        person_layout.addSpacerItem(spacer)

        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(lambda: self.remove_person(person.name, person_layout))
        person_layout.addWidget(remove_button)

        self.layout.addLayout(person_layout)

    def remove_person(self, name, layout):
        """
        Remove a person from the list and the UI.
        :param name: The name of the person to remove.
        :param layout: The layout corresponding to the person.
        """
        self.marked_persons.pop(name, None)

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.layout.removeItem(layout)

    def __contains__(self, item):
        return item in self.marked_persons

    def update_person(self, person):
        if person.name in self.marked_persons:
            self.marked_persons[person.name] = person
        else:
            self.add_person(person)

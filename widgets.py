import sys
import pandas as pd
from PyQt5 import QtWidgets, QtGui, QtCore


class AddRecordWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.fields = (
            "id",
            "radius_mean",
            "texture_mean",
            "perimeter_mean",
            "area_mean",
            "smoothness_mean",
            "compactness_mean",
            "concavity_mean",
            "concave points_mean",
            "symmetry_mean",
            "fractal_dimension_mean",
            "radius_se",
            "texture_se",
            "perimeter_se",
            "area_se",
            "smoothness_se",
            "compactness_se",
            "concavity_se",
            "concave points_se",
            "symmetry_se",
            "fractal_dimension_se",
            "radius_worst",
            "texture_worst",
            "perimeter_worst",
            "area_worst",
            "smoothness_worst",
            "compactness_worst",
            "concavity_worst",
            "concave points_worst",
            "symmetry_worst",
            "fractal_dimension_worst",
        )
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.scroll_area = QtWidgets.QScrollArea(self)
        self.scroll_inner = QtWidgets.QWidget()
        self.form_layout = QtWidgets.QFormLayout()
        self.open_file_button = QtWidgets.QPushButton("Выбрать файл", self)
        self.add_record_button = QtWidgets.QPushButton("Добавить запись", self)
        self.setup_form_layout()
        self.scroll_inner.setLayout(self.form_layout)
        self.scroll_area.setWidget(self.scroll_inner)
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.open_file_button)
        self.main_layout.addWidget(self.add_record_button)
        self.open_file_button.clicked.connect(self.fill_from_file)
        self.add_record_button.clicked.connect(self.get_dataframe)
        self.setWindowTitle("Добавить запись")
        self.resize(350, 500)

    def setup_form_layout(self):
        self.inputs = []
        double_validator = QtGui.QDoubleValidator(self)
        int_validator = QtGui.QIntValidator(self)
        for field in self.fields:
            line_edit = QtWidgets.QLineEdit(self)
            if field == "id":
                line_edit.setValidator(int_validator)
            else:
                line_edit.setValidator(double_validator)
            self.inputs.append(line_edit)
            self.form_layout.addRow(QtWidgets.QLabel(field, self), line_edit)
        self.delimiter_input = QtWidgets.QLineEdit(",", self)
        self.form_layout.addRow(QtWidgets.QLabel("Разделитель"), self.delimiter_input)

    def read_file(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self, "Выберите файл", "", "*.csv;; *.xlsx;; *.txt")[0]
        if not filename:
            return
        if filename.endswith(".xlsx"):
            data = pd.read_excel(filename)
        else:
            delimiter = self.delimiter_input.text()
            try:
                data = pd.read_csv(filename, delimiter=delimiter)
            except Exception:
                QtWidgets.QMessageBox.warning(self, "Ошибка!", "Некорректный разделитель")
                return
        return data

    def fill_from_file(self, data):
        if (data := self.read_file()) is None:
            return
        try:
            for index, field in enumerate(self.fields):
                self.inputs[index].setText(
                    str(data.iloc[0, data.columns.get_loc(field)]))
        except Exception:
            QtWidgets.QMessageBox.critical(
                self, "Ошибка!",
                "Невозможно прочитать выбранный файл.\n"
                "Возможно указан неверный разделитель")

    def get_dict(self):
        data = {}
        try:
            for index, field in enumerate(self.fields):
                data[field] = float(self.inputs[index].text().replace(",", "."))
                if field == "id":
                    data[field] = int(data[field])
            data["diagnosis"] = ""
        except ValueError:
            pass
        return data

    def get_dataframe(self):
        return pd.DataFrame(self.get_dict(), index=[0])

    def clear_inputs(self):
        for inp in self.inputs:
            inp.setText("")

    def closeEvent(self, event):
        self.clear_inputs()
        event.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = AddRecordWindow()
    window.show()
    sys.exit(app.exec())

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import numpy as np
import pandas as pd
import pickle
import sys
import csv
from widgets import *


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.user_filename = None
        self.model_filename = "model.pickle"
        try:
            self.load_model()
        except Exception as err:
            print(err)
            self.prepare_model()

    def setup_ui(self):
        vbox = QHBoxLayout()
        self.add_record_window = AddRecordWindow()
        self.add_record_window.setWindowModality(Qt.ApplicationModal)
        self.add_record_window.add_record_button.clicked.connect(self.add_record)
        menubar = self.menuBar()
        filemenu = menubar.addMenu('Меню')
        filemenu.addAction(self.create_open_action())
        filemenu.addAction(self.create_save_action())
        filemenu.addAction(self.create_add_record_action())
        self.tableWidget = QTableWidget()
        vbox.addWidget(self.tableWidget)
        centralWidget = QWidget()
        centralWidget.setLayout(vbox)
        self.setCentralWidget(centralWidget)
        self.tableWidget.resizeColumnsToContents()
        self.setWindowTitle("Analyzer")
        self.resize(500, 500)

    def create_open_action(self):
        fileAc = QAction('Открыть файл', self)
        fileAc.setShortcut('Ctrl+O')
        fileAc.triggered.connect(self.read_file)
        return fileAc

    def create_save_action(self):
        infoAc = QAction('Показать результат анализа и сохранить файл', self)
        infoAc.setShortcut('Ctrl+S')
        infoAc.triggered.connect(self.save_results)
        return infoAc

    def create_add_record_action(self):
        addAc = QAction("Добавить запись", self)
        addAc.setShortcut("Ctrl+N")
        addAc.triggered.connect(self.show_add_record_window)
        return addAc

    def save_model(self):
        with open(self.model_filename, "wb") as f:
            pickle.dump(self.tree, f)

    def load_model(self):
        with open(self.model_filename, "rb") as f:
            self.tree = pickle.load(f)

    def prepare_model(self):
        self.data = pd.read_csv('data.csv')

        for col in self.data['diagnosis']:
            self.data['diagnosis'].replace('M', 0, inplace=True)
            self.data['diagnosis'].replace('B', 1, inplace=True)

        self.data.drop(['Unnamed: 32'], inplace=True, axis=1)
        self.data.drop([
            'radius_mean',
            'perimeter_mean',
            'area_mean',
            'smoothness_mean',
            'compactness_mean',
            'concavity_mean',
            'symmetry_mean',
            'fractal_dimension_mean',
            'radius_se',
            'perimeter_se',
            'radius_se',
            'compactness_se',
            'texture_se',
            'perimeter_se',
            'compactness_se',
            'symmetry_se',
            'fractal_dimension_se',
            'perimeter_worst',
            'compactness_worst',
            'concave points_worst',
            'symmetry_worst',
            'fractal_dimension_worst'
        ], inplace=True, axis=1)
        np.random.seed(42)
        self.X = self.data.drop(['diagnosis'], axis=1)
        self.Y = self.data['diagnosis']
        self.X_train, self.X_test, self.Y_train, self.Y_test = train_test_split(self.X, self.Y, test_size=0.3)

        self.tree = DecisionTreeClassifier(max_depth=4)
        self.tree.fit(self.X_train, self.Y_train)
        self.save_model()

    def read_file(self):
        fname = QFileDialog.getOpenFileName(self, 'Выберите файл', '', '*.csv')[0]
        if not fname:
            return
        self.user_filename = fname
        with open(fname) as f:
            reader = csv.reader(f, delimiter=';')
            title = next(reader)
            self.tableWidget.setColumnCount(len(title))
            self.tableWidget.setHorizontalHeaderLabels(title)
            self.tableWidget.setRowCount(0)
            for i, row in enumerate(reader):
                self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(elem))

    def make_predictions(self):
        self.data_user = pd.read_csv(self.user_filename, sep=";")
        self.data_user.drop([
            'radius_mean',
            'perimeter_mean',
            'area_mean',
            'smoothness_mean',
            'compactness_mean',
            'concavity_mean',
            'symmetry_mean',
            'fractal_dimension_mean',
            'radius_se',
            'perimeter_se',
            'radius_se',
            'compactness_se',
            'texture_se',
            'perimeter_se',
            'compactness_se',
            'symmetry_se',
            'fractal_dimension_se',
            'perimeter_worst',
            'compactness_worst',
            'concave points_worst',
            'symmetry_worst',
            'fractal_dimension_worst'
        ], inplace=True, axis=1)

        self.data_user.drop(['Unnamed: 32'], inplace=True, axis=1)

        for col in self.data_user['diagnosis']:
            self.data_user['diagnosis'].replace('M', 2, inplace=True)
            self.data_user['diagnosis'].replace('B', 2, inplace=True)
            self.data_user['diagnosis'].replace('None', 2, inplace=True)

        self.X2 = self.data_user.drop(['diagnosis'], axis=1)
        self.tree_prediction = self.tree.predict(self.X2)

        self.tableWidget.resizeColumnsToContents()

    def save_results(self):
        self.make_predictions()
        self.listofmandb = ["B" if p == 1 else "M" for p in self.tree_prediction]
        for col in range(len(self.data_user['diagnosis'])):
            self.data_user.loc[col, 'diagnosis'] = self.listofmandb.pop(0)

        self.data_user.to_csv('result.csv', encoding='utf-8', index=None)

        with open('result.csv', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=',')
            title = next(reader)
            self.tableWidget.setColumnCount(len(title))
            self.tableWidget.setHorizontalHeaderLabels(title)
            self.tableWidget.setRowCount(0)
            for i, row in enumerate(reader):
                self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
                for j, elem in enumerate(row):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(elem))

        self.statusBar().showMessage('Программа работает с точностью - 93%')
        self.tableWidget.resizeColumnsToContents()

    def show_add_record_window(self):
        if self.user_filename:
            self.add_record_window.show()

    def add_record(self):
        data = self.add_record_window.get_dict()
        row_count = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_count)
        fields = list(self.add_record_window.fields)
        fields.insert(1, "diagnosis")
        for i, key in enumerate(fields):
            self.tableWidget.setItem(
                row_count, i, QTableWidgetItem(str(data.get(key, ""))))
        self.tableWidget.resizeColumnsToContents()
        self.add_record_window.close()
        self.add_row_to_user_file(data, fields)

    def add_row_to_user_file(self, data, fields):
        with open(self.user_filename, "a", encoding="u8") as f:
            writer = csv.writer(f, delimiter=";", lineterminator="\n")
            writer.writerow([data[f] for f in fields])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window()
    ex.show()
    sys.exit(app.exec_())

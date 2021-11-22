from PyQt5 import QtCore, QtGui, QtWidgets
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from detect_system_theme import detect
from utils import MT
from visualize import (
    plot_nerworth,
    plot_monthly_moneyflow,
    plot_expenses_by_category
)

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant(str(
                    self._data.iloc[index.row()][index.column()]))
        return QtCore.QVariant()

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None


class Ui_MainWindow:
    def setupUi(self, MainWindow):
        self.MT = MT()
        self.is_db_connected = False
        self.db_conn = None
        self.db_path = None
        self.MainWindow = MainWindow

        if detect() ==  "Dark":
            self.dark_mode()
        else:
            self.light_mode()

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 600)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("gui_assets/main_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setIconSize(QtCore.QSize(512, 512))

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        font = QtGui.QFont()
        font.setPointSize(16)

        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setFont(font)
        self.tabWidget.setObjectName("tabWidget")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.tabAccount = QtWidgets.QWidget()
        self.tabAccount.setObjectName("tabAccount")

        self.layoutAccount = QtWidgets.QGridLayout(self.tabAccount)
        self.layoutAccount.setObjectName("layoutAccount")

        self.labelConnected = QtWidgets.QLabel(self.tabAccount)
        self.labelConnected.setFont(font)
        self.labelConnected.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelConnected.setObjectName("labelConnected")
        self.layoutAccount.addWidget(self.labelConnected, 1, 0, 1, 1)

        self.labelPath = QtWidgets.QLabel(self.tabAccount)
        self.labelPath.setFont(font)
        self.labelPath.setStyleSheet("color: rgb(214, 39, 40);")
        self.labelPath.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.labelPath.setObjectName("labelPath")
        self.layoutAccount.addWidget(self.labelPath, 1, 1, 1, 1)

        self.ButtonNew = QtWidgets.QPushButton(self.tabAccount)
        self.ButtonNew.setFont(font)
        self.ButtonNew.setObjectName("ButtonNew")
        self.layoutAccount.addWidget(self.ButtonNew, 3, 0, 1, 2)
        self.ButtonNew.clicked.connect(self.new_db)

        self.ButtonOpen = QtWidgets.QPushButton(self.tabAccount)
        self.ButtonOpen.setFont(font)
        self.ButtonOpen.setObjectName("ButtonOpen")
        self.layoutAccount.addWidget(self.ButtonOpen, 4, 0, 1, 2)
        self.ButtonOpen.clicked.connect(self.connect_db)

        self.ButtonTerminate = QtWidgets.QPushButton(self.tabAccount)
        self.ButtonTerminate.setFont(font)
        self.ButtonTerminate.setObjectName("ButtonTerminate")
        self.layoutAccount.addWidget(self.ButtonTerminate, 5, 0, 1, 2)
        self.ButtonTerminate.clicked.connect(self.terminate_connection)

        self.tabWidget.addTab(self.tabAccount, "")

        self.tabData = QtWidgets.QWidget()
        self.tabData.setObjectName("tabData")
        self.layoutData = QtWidgets.QGridLayout(self.tabData)
        self.layoutData.setObjectName("layoutData")
        self.tableView = QtWidgets.QTableView(self.tabData)
        self.tableView.setObjectName("tableView")
        self.tableView.setFont(font)
        self.tableView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.layoutData.addWidget(self.tableView, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tabData, "")

        self.tabNetflow = QtWidgets.QWidget()
        self.tabNetflow.setObjectName("tabNetflow")
        self.layoutNetflow = QtWidgets.QGridLayout(self.tabNetflow)
        self.layoutNetflow.setObjectName("layoutNetflow")

        self.netflowYearLabel = QtWidgets.QLabel(self.tabNetflow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.netflowYearLabel.sizePolicy().hasHeightForWidth())
        self.netflowYearLabel.setSizePolicy(sizePolicy)
        # self.netflowYearLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.netflowYearLabel.setObjectName("netflowYearLabel")
        self.netflowYearLabel.setFont(font)
        self.layoutNetflow.addWidget(self.netflowYearLabel, 0, 0, 1, 1)

        self.netflowYearComboBox = QtWidgets.QComboBox(self.tabNetflow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.netflowYearComboBox.sizePolicy().hasHeightForWidth())
        self.netflowYearComboBox.setSizePolicy(sizePolicy)
        self.netflowYearComboBox.setObjectName("netflowYearComboBox")
        self.netflowYearComboBox.setFont(font)
        self.layoutNetflow.addWidget(self.netflowYearComboBox, 0, 1, 1, 1)
        self.netflowYearComboBox.currentIndexChanged.connect(self.update_yearly_netflow)

        self.netflowPlot = MplCanvas(self.tabNetflow)
        self.netflowPlot.setObjectName("netflowPlot")
        self.layoutNetflow.addWidget(self.netflowPlot, 1, 0, 1, 2)

        self.tabWidget.addTab(self.tabNetflow, "")

        self.tabWidget.setTabEnabled(1, False)
        self.tabWidget.setTabEnabled(2, False)

        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)

        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")

        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")

        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.actionConnect = QtWidgets.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("gui_assets/database.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionConnect.setIcon(icon1)
        self.actionConnect.setObjectName("actionConnect")
        self.actionConnect.triggered.connect(self.connect_db)

        self.actionLight_Mode = QtWidgets.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("gui_assets/light_mode.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionLight_Mode.setIcon(icon3)
        self.actionLight_Mode.setObjectName("actionLight_Mode")
        self.actionLight_Mode.triggered.connect(self.light_mode)

        self.actionDark_Mode = QtWidgets.QAction(MainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap("gui_assets/dark_mode.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDark_Mode.setIcon(icon4)
        self.actionDark_Mode.setObjectName("actionDark_Mode")
        self.actionDark_Mode.triggered.connect(self.dark_mode)

        self.actionAbout = QtWidgets.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("gui_assets/about.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionAbout.setIcon(icon2)
        self.actionAbout.setObjectName("actionAbout")

        self.menuFile.addAction(self.actionConnect)
        self.menuHelp.addAction(self.actionAbout)
        self.menuView.addAction(self.actionLight_Mode)
        self.menuView.addAction(self.actionDark_Mode)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Money Tracker v1.0"))
        self.ButtonNew.setText(_translate("MainWindow", "Start a new account"))
        self.labelPath.setText(_translate("MainWindow", "None"))
        self.labelConnected.setText(_translate("MainWindow", "Current Connected Account:"))
        self.ButtonOpen.setText(_translate("MainWindow", "Connect an existing account"))
        self.ButtonTerminate.setText(_translate("MainWindow", "Terminate the connection"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabAccount), _translate("MainWindow", "Account"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabData), _translate("MainWindow", "Data"))
        self.netflowYearLabel.setText(_translate("MainWindow", "Year: "))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabNetflow), _translate("MainWindow", "Netflow"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionConnect.setText(_translate("MainWindow", "Connect Database"))
        self.actionConnect.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionLight_Mode.setText(_translate("MainWindow", "Light Mode"))
        self.actionDark_Mode.setText(_translate("MainWindow", "Dark Mode"))

    def light_mode(self):
        global APP
        with open("./gui_assets/Breeze/light/stylesheet.qss", "r") as f:
            stylesheet = f.read()
            APP.setStyleSheet(stylesheet)

    def dark_mode(self):
        global APP
        with open("./gui_assets/Breeze/dark/stylesheet.qss", "r") as f:
            stylesheet = f.read()
            APP.setStyleSheet(stylesheet)

    def connect_db(self):
        name = QtWidgets.QFileDialog.getOpenFileName(self.MainWindow, "Open Database", filter="*.db")
        self.db_path = name[0]
        self.db_conn = self.MT.open_db(path=self.db_path)
        self.is_db_connected = True
        self.update()

    def new_db(self):
        name = QtWidgets.QFileDialog.getSaveFileName(self.MainWindow, "New Database", filter="SQLite Database (*.db)")
        self.db_path = name[0]
        self.db_conn = self.MT.open_db(path=self.db_path)
        self.is_db_connected = True
        self.MT.initialize_database()
        self.update()

    def terminate_connection(self):
        self.db_path = None
        self.is_db_connected = False
        if self.MT is not None:
            self.MT.close()
        self.update()

    def update(self):
        if not self.is_db_connected:
            self.db_conn = None
            self.labelPath.setText("None")
            self.labelPath.setStyleSheet("color: rgb(214, 39, 40);")
            self.tabWidget.setTabEnabled(1, False)
            self.tabWidget.setTabEnabled(2, False)
        else:
            self.labelPath.setText(self.db_path)
            self.labelPath.setStyleSheet("color: rgb(31, 119, 180);")
            self.tabWidget.setTabEnabled(1, True)
            self.tabWidget.setTabEnabled(2, True)
            self.populate_data_table()
            years = self.MT.get_years()
            self.netflowYearComboBox.clear() # FIXME: triggers update netflow :(
            self.netflowYearComboBox.addItems(years)
            self.update_plots()

    def populate_data_table(self):
        df = self.MT.get_transactions_df_custom("""
            SELECT rowid, * FROM transactions
            ORDER BY date DESC
        """)
        model = PandasModel(df)
        self.tableView.setModel(model)

    def update_plots(self):
        self.update_yearly_netflow()

    def update_yearly_netflow(self):
        year = int(self.netflowYearComboBox.currentText())
        self.netflowPlot.axes.cla()
        ax = self.netflowPlot.axes
        plot_nerworth(ax, self.MT, 2021)
        self.netflowPlot.draw()

    def closeEvent(self, event):
        self.terminate_connection()
        print("Closing")


class MainWindowCustom(QtWidgets.QMainWindow):
    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(
            self, "Message",
            "Are you sure you want to quit? Any unsaved work will be lost.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()



if __name__ == "__main__":
    import sys
    APP = QtWidgets.QApplication(sys.argv)
    MainWindow = MainWindowCustom()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(APP.exec_())

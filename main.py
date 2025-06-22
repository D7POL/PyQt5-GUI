import sys
from PyQt5.QtWidgets import QApplication
from Login.Login import LoginFenster

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenster = LoginFenster()
    fenster.show()
    sys.exit(app.exec_())

import sys
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer
from gui.login import LoginFenster

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('tooth_logo.png'))

    # Splash Screen erstellen
    pixmap = QPixmap("start.png")
    splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
    splash.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
    splash.show()

    # Hauptfenster im Hintergrund erstellen
    fenster = LoginFenster()

    # Funktion, um den Splash Screen zu schließen und das Hauptfenster anzuzeigen
    def show_main_window():
        splash.close()
        fenster.show()

    # Timer starten, der die Funktion nach 3000 Millisekunden (3 Sekunden) aufruft
    QTimer.singleShot(4000, show_main_window)

    sys.exit(app.exec_())

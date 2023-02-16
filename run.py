from app_objects.main_widget import Widget
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon

if __name__ == "__main__":
    #app object and style
    app = QApplication()
    with open("assets/style.qss","r") as style:
        app.setStyleSheet(style.read())
    
    #tray and app widget
    tray = QSystemTrayIcon()
    tray.setIcon(QIcon("assets/tray.png"))	
    main_widget = Widget()
    	
    def main_control( ) -> None:
        """
        main_contorl hide or show the widget when System Volume action is clicked.
        """
        if main_widget.isHidden():
            main_widget.show()
            
        else:
            main_widget.hide()

    #menu and actions
    menu = QMenu()
    menu.addAction("System Volume", main_control)
    menu.addAction("Quit",main_widget.force_quit) 
    
    tray.setContextMenu(menu)
    tray.show()
    
    app.exec()

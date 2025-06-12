 Per testare la finestra di selezione (puoi aggiungere questo in un file di test separato o nel main temporaneamente)
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    dialog = SelezionaMaterialeDisponibile()
    if dialog.exec() == QDialog.Accepted:
        print("Materiale selezionato:", dialog.materiale_scelto)
    else:
        print("Selezione annullata.")
    sys.exit(app.exec())
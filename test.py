from concurrent.futures import ThreadPoolExecutor
from scanner import identify_content
from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
import os
import sys
import time


# ThreadPool scanner 0.6s/10k
path = os.path.expandvars(r"%temp%\Roblox\http")
files = [os.path.join(path, f) for f in os.listdir(path)]

def identify(file_path):
    return os.path.basename(file_path), identify_content(file_path)

start = time.time()
with ThreadPoolExecutor(max_workers=64) as executor:
    results = list(executor.map(identify, files))

print(f"Time: {time.time() - start:.2f}s")


# Pyside6 Table thing
app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Scan Results")

table = QTableWidget()
table.setRowCount(len(results))
table.setColumnCount(2)
table.setHorizontalHeaderLabels(["File Name", "Detected Type"])

for row, (filename, file_type) in enumerate(results):
    table.setItem(row, 0, QTableWidgetItem(filename))
    table.setItem(row, 1, QTableWidgetItem(file_type))

layout = QVBoxLayout()
layout.addWidget(table)
window.setLayout(layout)
window.resize(600, 400)
window.show()

sys.exit(app.exec())
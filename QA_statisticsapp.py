import sys
import os
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from scipy import stats


def clean_numeric(series):
    return pd.to_numeric(series.astype(str).str.replace(",", ".").str.strip(), errors="coerce")


def levene_test(a, b):
    stat, p = stats.levene(a, b)
    if p < 0.05:
        return "Variances are statistically different. Consider using the Welch test.", p
    else:
        return "Variances are NOT statistically different. Proceed with the t-test.", p


def ttest(a, b, equalvar=True):
    stat, p = stats.ttest_ind(a, b, equal_var=equalvar)
    if p < 0.05:
        return "Means are statistically different.", p
    else:
        return "Means are NOT statistically different.", p


def welch(a, b):
    stat, p = stats.ttest_ind(a, b, equal_var=False)
    if p < 0.05:
        return "Means are statistically different (Welch).", p
    else:
        return "Means are NOT statistically different (Welch).", p


def confidence_interval(a, b, alpha=0.05):
    n1, n2 = len(a), len(b)
    mean1, mean2 = np.mean(a), np.mean(b)
    var1, var2 = np.var(a, ddof=1), np.var(b, ddof=1)
    diff = mean1 - mean2
    _, p_levene = stats.levene(a, b)

    if p_levene < 0.05:
        se = np.sqrt(var1/n1 + var2/n2)
        df = (var1/n1 + var2/n2)**2 / ((var1**2)/(n1**2 * (n1 - 1)) + (var2**2)/(n2**2 * (n2 - 1)))
        method = "Welch (unequal variances)"
    else:
        pooled_var = ((n1 - 1)*var1 + (n2 - 1)*var2) / (n1 + n2 - 2)
        se = np.sqrt(pooled_var * (1/n1 + 1/n2))
        df = n1 + n2 - 2
        method = "Student (equal variances)"

    t_crit = stats.t.ppf(1 - alpha/2, df)
    ci_low = diff - t_crit * se
    ci_high = diff + t_crit * se

    return f"""Method: {method}
Difference in means: {diff:.2f}
{int((1 - alpha) * 100)}% Confidence Interval: [{ci_low:.2f}, {ci_high:.2f}]
Degrees of freedom (df): {df:.2f}"""


class QA_Statistics(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Statistics with Filtering")
        self.setGeometry(200, 100, 750, 600)

        self.df = pd.DataFrame()
        self.group1 = []
        self.group2 = []

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # === Output box with background image ===
        output_container = QWidget()
        output_container.setStyleSheet("""
            QWidget {
                background-image: url('west_mani.jpg');
                background-repeat: no-repeat;
                background-position: center;
                background-size: cover;
                border-radius: 8px;
            }
        """)
        output_layout = QVBoxLayout()
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 0, 0, 0.4);
                font-family: Courier New, monospace;
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.9);
                border-radius: 6px;
                padding: 12px;
            }
        """)
        output_layout.addWidget(self.output)
        output_container.setLayout(output_layout)
        layout.addWidget(output_container)

        file_layout = QHBoxLayout()
        self.load_button = QPushButton("Load Excel File")
        self.sheet_combo = QComboBox()
        self.sheet_combo.currentTextChanged.connect(self.sheet_selected)
        file_layout.addWidget(self.load_button)
        file_layout.addWidget(QLabel("Sheet:"))
        file_layout.addWidget(self.sheet_combo)
        layout.addLayout(file_layout)

        filter_layout = QHBoxLayout()
        self.filter_column = QComboBox()
        self.filter_value1 = QComboBox()
        self.filter_value2 = QComboBox()
        filter_layout.addWidget(QLabel("Filter by:"))
        filter_layout.addWidget(self.filter_column)
        filter_layout.addWidget(QLabel("Group A:"))
        filter_layout.addWidget(self.filter_value1)
        filter_layout.addWidget(QLabel("Group B:"))
        filter_layout.addWidget(self.filter_value2)
        layout.addLayout(filter_layout)

        target_layout = QHBoxLayout()
        self.target_column = QComboBox()
        target_layout.addWidget(QLabel("Compare variable:"))
        target_layout.addWidget(self.target_column)
        layout.addLayout(target_layout)

        alpha_layout = QHBoxLayout()
        self.alpha_combo = QComboBox()
        self.alpha_combo.addItems(["90%", "95%", "99%"])
        alpha_layout.addWidget(QLabel("Confidence Level:"))
        alpha_layout.addWidget(self.alpha_combo)
        layout.addLayout(alpha_layout)

        button_layout = QHBoxLayout()
        self.levene_button = QPushButton("Levene Test")
        self.ttest_button = QPushButton("T-Test")
        self.welch_button = QPushButton("Welch Test")
        self.ci_button = QPushButton("Confidence Interval")
        self.clear_button = QPushButton("Clear")
        for btn in [self.levene_button, self.ttest_button, self.welch_button, self.ci_button, self.clear_button]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 8px 14px;
                    border-radius: 6px;
                    box-shadow: 3px 3px 8px rgba(0, 0, 0, 0.3);
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)
        central_widget.setLayout(layout)

        self.bg_button = QPushButton("Change Background")
        self.bg_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 14px;
                border-radius: 6px;
                box-shadow: 3px 3px 8px rgba(0, 0, 0, 0.3);
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        button_layout.addWidget(self.bg_button)
        self.bg_button.clicked.connect(self.change_background)
        
        
        
        self.load_button.clicked.connect(self.load_excel)
        self.levene_button.clicked.connect(self.run_levene)
        self.ttest_button.clicked.connect(self.run_ttest)
        self.welch_button.clicked.connect(self.run_welch)
        self.ci_button.clicked.connect(self.run_ci)
        self.clear_button.clicked.connect(lambda: self.output.clear())

    def load_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx)")
        if file_path:
            xls = pd.ExcelFile(file_path)
            self.sheet_combo.clear()
            self.sheet_combo.addItems(xls.sheet_names)
            self.excel_data = xls

    def sheet_selected(self, sheet_name):
        try:
            self.df = self.excel_data.parse(sheet_name)
            columns = self.df.columns.astype(str).tolist()
            self.filter_column.clear()
            self.filter_column.addItems(columns)
            self.target_column.clear()
            self.target_column.addItems(columns)
            self.filter_column.currentTextChanged.connect(self.update_filter_values)
            self.update_filter_values()
            self.output.append(f"Sheet '{sheet_name}' loaded. Select filter and variable.")
        except Exception as e:
            self.output.append(f"Error loading sheet: {e}")

    def update_filter_values(self):
        col = self.filter_column.currentText()
        if col:
            values = self.df[col].dropna().unique().astype(str)
            self.filter_value1.clear()
            self.filter_value2.clear()
            self.filter_value1.addItems(values)
            self.filter_value2.addItems(values)

    def prepare_filtered_data(self):
        filter_col = self.filter_column.currentText()
        val1 = self.filter_value1.currentText()
        val2 = self.filter_value2.currentText()
        target = self.target_column.currentText()

        if val1 == val2:
            self.output.append("❌ Please select two different group values.")
            return False

        try:
            group_a = self.df[self.df[filter_col].astype(str) == val1]
            group_b = self.df[self.df[filter_col].astype(str) == val2]

            a = clean_numeric(group_a[target])
            b = clean_numeric(group_b[target])
            a = a.dropna()
            b = b.dropna()

            if len(a) == 0 or len(b) == 0:
                self.output.append("❌ One of the groups has no numeric data.")
                return False

            self.group1 = a.values
            self.group2 = b.values
            return True

        except Exception as e:
            self.output.append(f"Error filtering data: {e}")
            return False

    def run_levene(self):
        if self.prepare_filtered_data():
            result, p = levene_test(self.group1, self.group2)
            self.output.append(f"\n[Levene Test]\n{result}\np-value: {p:.4f}")

    def run_ttest(self):
        if self.prepare_filtered_data():
            p_levene = stats.levene(self.group1, self.group2)[1]
            equal = p_levene >= 0.05
            result, p = ttest(self.group1, self.group2, equalvar=equal)
            self.output.append(f"\n[T-Test]\n{result}\np-value: {p:.4f}")

    def run_welch(self):
        if self.prepare_filtered_data():
            result, p = welch(self.group1, self.group2)
            self.output.append(f"\n[Welch Test]\n{result}\np-value: {p:.4f}")

    def run_ci(self):
        if self.prepare_filtered_data():
            selected = self.alpha_combo.currentText()
            if selected == "90%":
                alpha = 0.10
            elif selected == "99%":
                alpha = 0.01
            else:
                alpha = 0.05
            result = confidence_interval(self.group1, self.group2, alpha=alpha)
            self.output.append(f"\n[Confidence Interval — {selected}]\n{result}")

    def change_background(self):
        dialog = QFileDialog(self)
        dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")
        dialog.setViewMode(QFileDialog.Detail)  # QFileDialog.List if preferred
    
        if dialog.exec_():
            file_path = dialog.selectedFiles()[0]
            css_path = file_path.replace("\\", "/")
            self.centralWidget().findChild(QWidget).setStyleSheet(f"""
    QWidget {{
        background-image: url('{css_path}');
        background-repeat: no-repeat;
        background-position: center center;
        background-attachment: fixed;
        background-size: cover;
        border-radius: 8px;
    }}
""")






if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QA_Statistics()
    window.show()
    sys.exit(app.exec_())

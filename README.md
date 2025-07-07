# Stats
Stats_app
 QA Statistics App
QA Statistics App is a user-friendly GUI tool built with PyQt5 that allows users to load Excel datasets and perform fundamental statistical tests for comparing two groups based on a selected filter and target variable.

✨ Features
Load Excel files and select specific sheets

Choose a filter column and define two comparison groups (Group A vs Group B)

Select a numeric variable (e.g., weight, score) to compare between the groups

Perform key statistical tests:

Levene’s Test for equality of variances

Student’s t-Test (equal variances)

Welch’s t-Test (unequal variances)

Confidence Interval for the difference in means

Customize confidence level (90%, 95%, 99%)

Styled output panel with transparent overlay and background image

Option to change background image dynamically from within the app

🧪 Technical Highlights
Built with PyQt5 for cross-platform GUI

Uses pandas and scipy.stats for data handling and statistical testing

Supports numerical data cleaning (comma-to-dot conversion, trimming, etc.)

Clean and modular structure for easy extension or integration

📁 Requirements
Python 3.x

PyQt5

pandas

scipy

numpy

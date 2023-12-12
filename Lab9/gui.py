import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
                             QTextEdit, QPushButton, QFileDialog, QMessageBox)
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ftplib import FTP
import os
from dotenv import load_dotenv

load_dotenv()
# Function to send an email
def send_email(destination_email, subject, email_text, file_link):
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = destination_email
    message['Subject'] = subject
    message.attach(MIMEText(email_text + "\n\nFile link: " + file_link, 'plain'))

    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(sender_email, sender_password)
    session.sendmail(sender_email, destination_email, message.as_string())
    session.quit()

# Function to upload a file via FTP
def upload_file_ftp(file_path):
    ftp_server = "138.68.98.108"
    username = "yourusername"
    password = "yourusername"
    remote_path = "/home/somedirectory/FAF-211/coretchi_mihai/"

    remote_file_path = remote_path + file_path.split('/')[-1]

    ftp = FTP(ftp_server)
    ftp.login(username, password)
    with open(file_path, 'rb') as file:
        ftp.storbinary(f'STOR {remote_file_path}', file)
    ftp.quit()

    web_accessible_path = "/FAF-211/coretchi_mihai/" + file_path.split('/')[-1]
    return "http://138.68.98.108" + web_accessible_path

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Email Sender UI'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)

        layout = QVBoxLayout()

        self.destination_email_edit = QLineEdit(self)
        layout.addWidget(QLabel('Enter destination email:'))
        layout.addWidget(self.destination_email_edit)

        self.subject_edit = QLineEdit(self)
        layout.addWidget(QLabel('Enter email subject:'))
        layout.addWidget(self.subject_edit)

        self.email_text_edit = QTextEdit(self)
        layout.addWidget(QLabel('Enter email text:'))
        layout.addWidget(self.email_text_edit)

        self.file_path_edit = QLineEdit(self)
        layout.addWidget(QLabel('Enter path to the file to upload:'))
        layout.addWidget(self.file_path_edit)

        browse_button = QPushButton('Browse', self)
        browse_button.clicked.connect(self.browse_file)
        layout.addWidget(browse_button)

        submit_button = QPushButton('Send Email', self)
        submit_button.clicked.connect(self.submit)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def browse_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open file', '/home')
        if filename:
            self.file_path_edit.setText(filename)

    def submit(self):
        destination_email = self.destination_email_edit.text()
        subject = self.subject_edit.text()
        email_text = self.email_text_edit.toPlainText()
        file_path = self.file_path_edit.text()

        try:
            file_link = upload_file_ftp(file_path)
            send_email(destination_email, subject, email_text, file_link)
            QMessageBox.information(self, 'Success', 'Email has been sent successfully!')
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())

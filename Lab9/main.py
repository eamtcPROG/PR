from flask import Flask, request, render_template, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ftplib import FTP

# Function to send an email
def send_email(destination_email, subject, email_text, file_link):
    sender_email = ""
    sender_password = ""  # Replace with your password

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
    password = "yourpassword"
    remote_path = "/home/somedirectory/FAF-211/grama/"

    remote_file_path = remote_path + file_path.split('/')[-1]

    ftp = FTP(ftp_server)
    ftp.login(username, password)
    with open(file_path, 'rb') as file:
        ftp.storbinary(f'STOR {remote_file_path}', file)
    ftp.quit()

    web_accessible_path = "/FAF-211/grama/" + file_path.split('/')[-1]
    return "http://138.68.98.108" + web_accessible_path

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set your secret key here
app.config['UPLOAD_FOLDER'] = 'uploads'  # Temporary upload folder

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        destination_email = request.form['destination_email']
        subject = request.form['subject']
        email_text = request.form['email_text']
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            try:
                file_link = upload_file_ftp(file_path)
                send_email(destination_email, subject, email_text, file_link)
                flash('Email has been sent successfully!')
            except Exception as e:
                flash(str(e))
            finally:
                os.remove(file_path)
        else:
            flash('No file selected')

        return redirect(url_for('index'))

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

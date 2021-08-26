import smtplib
from email.mime.multipart import MIMEMultipart  # email內容載體
from email.mime.text import MIMEText  # 用於製作文字內文
from email.mime.base import MIMEBase  # 用於承載附檔
from email import encoders  # 用於附檔編碼
import datetime


# start_date = date[0], end_date=date[7]
def email_sender(start_date, end_date, year, week_num, report_date):
    # read the list of recipients
    f = open("list.txt")
    lines = f.read().splitlines()
    print(lines)

    # Email Account
    email_sender_account = "pythonnotificantionbot@gmail.com"  # your email
    email_sender_username = "pythonnotificantionbot@gmail.com"  # your email username
    email_sender_password = "tecopythonproject"  # your email password
    email_smtp_server = "smtp.gmail.com"  # change if not gmail.
    email_smtp_port = 587  # change if needed.
    email_recepients = lines  # your recipients
    f.close()

    # 設定信件內容與收件人資訊
    Subject = "中壢二廠 VPI含浸爐 設備稼動週報表"
    contents = """
    報表自動推播
    中壢二廠 VPI含浸爐 設備稼動週報表
    統計時間：""" + start_date + "~" + end_date

    # 設定附件（可設多個）
    attachments = ["VPI含浸爐_設備稼動週報表_" + year + "_" + week_num + "_" + report_date + ".xlsx"]

    server = smtplib.SMTP(email_smtp_server, email_smtp_port)
    print(f"Logging in to {email_sender_account}")
    server.starttls()
    server.login(email_sender_username, email_sender_password)

    for recipient in email_recepients:
        print(f"Sending email to {recipient}")
        message = MIMEMultipart()
        message['From'] = email_sender_account
        message['To'] = recipient
        message['Subject'] = Subject
        message.attach(MIMEText(contents))
        for file in attachments:
            with open(file, 'rb') as fp:
                add_file = MIMEBase('application', "octet-stream")
                add_file.set_payload(fp.read())
                encoders.encode_base64(add_file)
                add_file.add_header('Content-Disposition', 'attachment',
                                    filename=file)
                message.attach(add_file)
        server.sendmail(email_sender_account, recipient, message.as_string())

    server.quit()
    print("信件發送成功")


def email_sender_m(start_date, end_date, year, week_num, month, report_date):
    # read the list of recipients
    f = open("list.txt")
    lines = f.read().splitlines()
    print(lines)

    # Email Account
    email_sender_account = "pythonnotificantionbot@gmail.com"  # your email
    email_sender_username = "pythonnotificantionbot@gmail.com"  # your email username
    email_sender_password = "tecopythonproject"  # your email password
    email_smtp_server = "smtp.gmail.com"  # change if not gmail.
    email_smtp_port = 587  # change if needed.
    email_recepients = lines  # your recipients
    f.close()

    # 設定信件內容與收件人資訊
    Subject = "中壢二廠 VPI含浸爐 設備稼動週/月報表"
    contents = """
    報表自動推播
    中壢二廠 VPI含浸爐 設備稼動週/月報表
    統計時間：""" + start_date + "~" + end_date + "," + month + "月報表"

    # 設定附件（可設多個）
    attachments = ["VPI含浸爐_設備稼動週報表_" + year + "_" + week_num + "_" + report_date + ".xlsx",
                   "VPI含浸爐_設備稼動月報表_" + year + "_" + month + "_" + report_date + ".xlsx"]

    server = smtplib.SMTP(email_smtp_server, email_smtp_port)
    print(f"Logging in to {email_sender_account}")
    server.starttls()
    server.login(email_sender_username, email_sender_password)

    for recipient in email_recepients:
        print(f"Sending email to {recipient}")
        message = MIMEMultipart()
        message['From'] = email_sender_account
        message['To'] = recipient
        message['Subject'] = Subject
        message.attach(MIMEText(contents))
        for file in attachments:
            with open(file, 'rb') as fp:
                add_file = MIMEBase('application', "octet-stream")
                add_file.set_payload(fp.read())
                encoders.encode_base64(add_file)
                add_file.add_header('Content-Disposition', 'attachment', filename=file)
                message.attach(add_file)
        server.sendmail(email_sender_account, recipient, message.as_string())

    server.quit()
    print("信件發送成功")

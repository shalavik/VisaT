import smtplib

# Example usage
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login("your_email@gmail.com", "your_password")
server.sendmail("your_email@gmail.com", "receiver_email@gmail.com", "Hello from Python!")
server.quit()

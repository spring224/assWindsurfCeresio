import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Parametri del server SMTP
smtp_server = "smtps.aruba.it"  # In alternativa, smtp.aruba.it (non consigliato)
smtp_port = 465  # In alternativa, 25 (non consigliato)
email_address = "info@circolonauticoporlezza.com"
email_password = "Foil2025!"

# Crea il messaggio
msg = MIMEMultipart()
msg["From"] = email_address
msg["To"] = "marcosironi71@gmail.com"
msg["Subject"] = "test Invio Mail aii soci del circolo"
body = "al momento è un test di invio email ai soci del circolo nautico porlezza ," \
"devi pagare 35 MilIONI di  € per il rinnovo della tessera 2025, grazie PS se stasera ti vuoi fermare" \
"prima di andare a casa ti offro una birra, ciao Marco Sironi"
msg.attach(MIMEText(body, "plain"))

try:
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.login(email_address, email_password)

    # IMPORTANTE: invia al destinatario corretto
    server.sendmail(email_address, msg["To"], msg.as_string())
    print("Email inviata con successo!")

except Exception as e:
    print(f"Errore durante l'invio dell'email: {e}")
finally:
    server.quit()
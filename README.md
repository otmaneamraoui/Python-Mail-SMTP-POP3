# 📧 Python Mail — SMTP & POP3 from Scratch

A full implementation of **SMTP** and **POP3** email protocols built entirely in Python using raw TCP sockets — no external libraries, no `smtplib`, no `poplib`. Everything is implemented from the ground up following the RFC standards.

---

## 🗂️ Project Structure

```
projet_mail/
│
├── main.py                    # Entry point — choose SMTP or POP3 server
│
├── serveur/
│   ├── smtp_server.py         # SMTP server (port 2525)
│   └── pop3_server.py         # POP3 server (port 1100)
│
├── client/
│   ├── smtp_client.py         # SMTP client — send emails
│   └── pop3_client.py         # POP3 client — read emails (interactive menu)
│
├── mailboxes/
│   ├── alice@upssitech.fr.txt # Alice's mailbox
│   └── bob@upssitech.fr.txt   # Bob's mailbox
│
└── users.txt                  # User credentials (user:password)
```

---

## ⚙️ Features

### 📤 SMTP Server (port 2525)
Supports the following commands:
| Command | Description |
|---------|-------------|
| `HELO` | Client greeting |
| `EHLO` | Extended greeting (returns 502 — not implemented) |
| `MAIL FROM:<addr>` | Set sender address |
| `RCPT TO:<addr>` | Set recipient address |
| `DATA` | Start message body input |
| `RSET` | Reset current transaction |
| `NOOP` | Keep-alive / no-operation |
| `HELP` | List supported commands |
| `QUIT` | Close connection |

Emails are saved as `.txt` files in the `mailboxes/` directory, one file per recipient.

### 📥 POP3 Server (port 1100)
Supports the following commands:
| Command | Description |
|---------|-------------|
| `USER` | Provide username |
| `PASS` | Provide password |
| `STAT` | Mailbox status (message count + size) |
| `LIST` | List messages with sizes |
| `RETR n` | Retrieve full message #n |
| `TOP n k` | Preview first k lines of message #n |
| `UIDL` | Unique ID listing |
| `CAPA` | Server capabilities |
| `NOOP` | No-operation |
| `QUIT` | End session |

Authentication is handled via `users.txt` (format: `user:password`).

---

## 🚀 Getting Started

### Requirements
- Python 3.x
- No external dependencies

### Run the server

```bash
python main.py
```

Choose:
- `1` → Start the SMTP server (port 2525)
- `2` → Start the POP3 server (port 1100)

### Send an email (SMTP client)

In a separate terminal:

```bash
python client/smtp_client.py
```

Enter sender, recipient, subject, and body. End the message with a `.` on its own line.

### Read emails (POP3 client)

```bash
python client/pop3_client.py
```

Log in with one of the test accounts and use the interactive menu.

---

## 👤 Test Accounts

| Email | Password |
|-------|----------|
| `alice@upssitech.fr` | `azerty` |
| `bob@upssitech.fr` | `1234` |

---

## 🔄 How It Works

```
SMTP Flow:
  Client → HELO → MAIL FROM → RCPT TO → DATA → [message] → . → QUIT
  Server saves the email to mailboxes/<recipient>.txt

POP3 Flow:
  Client → USER → PASS → STAT/LIST/RETR → QUIT
  Server reads from mailboxes/<recipient>.txt
```

---

## 👨‍💻 Author

Project developed by:
- **AMRAOUI Otmane** — 1A/STRI

Academic project — University Paul Sabatier, Toulouse.

---

## 📜 License

Academic project — Not intended for commercial use.

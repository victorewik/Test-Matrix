# Test-Matrix Bot
A simple [maubot](https://github.com/maubot/maubot) fork from echo bot that pings and see some info.

This project is a fork of maubot/echo, originally licensed under MIT. Modifications and new features are licensed under AGPLv3.

Test Bot features:

  - Dual-End Diagnostics: Analyzes both the Sender (User) and the Receiver (Bot
    Server).
  - Point-to-Point Latency: Measures the exact travel time of the message across
    the Matrix federation.
  - Automatic IP Resolution:
      - Sender: Performs a DNS lookup on the user's homeserver to identify the
        originating IP and its geographic location.
      - Receiver: Shows the bot's public IP and host location.
  - Precise Timestamping: Displays exact dates and times for both "Sent" and
    "Received" events to debug synchronization issues.
  - Zero-Prefix Trigger: Responds to the word test (case-insensitive) without
    requiring any command prefix like !.
  - Clean UI: Minimalist English interface using professional HTML styling,
    optimized for all Matrix clients (Element, SchildiChat, etc.).

#🛠 Installation

1.  Download the testbot.mbp file from the releases section.
2.  Alternatively, build it yourself by zipping the source files: python3 -m
    zipfile -c testbot.mbp test.py maubot.yaml
3.  Upload the .mbp file to your Maubot management panel.
4.  Create an instance and link it to your Matrix account.

## 📖 Usage

Simply type the following in any room where the bot is present: test

The bot will reply with a detailed report:

```
✅ Test successful
Message received by server

SENDER USER INFO

  - User: @user:example.com
  - Sender Server: example.com
  - Sent at: 2026-05-21 04:12:58
  - Sender IP: 93.184.216.34
  - Location: United States

RECEIVER SERVER INFO

  - Latency: 111 ms
  - Server: victorewik.es
  - Received at: 2026-05-21 04:12:59
  - Server IP: XX.XXX.XXX.XX
  - Location: Spain
```

Technical Details

  - ID: es.victorewik.testbot
  - License: AGPL V3.0
  - Language: Python
  - Platform: Maubot / Mautrix-python

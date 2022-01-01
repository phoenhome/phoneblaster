# ☎️ Phone Blaster

#### Description

A script to dial a phone number and perform defined TwiML actions using Twilio with optional downloading of audio recordings and call metadata. 

#### Requirements

* Python 3
* Twilio Account
  * Phone Number
  * Account SID
  * Auth Token

#### Installation

Create a Python virtual environment:

`cd phoneblaster`

`python3 -m venv venv`

`source venv/bin/activate`

Install Python library dependencies:

`pip install -r requirements.txt`

#### Environment Variables

Environment variables can be set in a `.env` file:

`cp .env.example .env`

```
PHONEBLASTER_TWILIO_ACCOUNT_SID="ABCDEFGHIJKLMNOPQRSTUVWXYZ01234567"
PHONEBLASTER_TWILIO_AUTH_TOKEN="1234567890abcdefghijklmnopqrstuv"
PHONEBLASTER_CALL_TWILIO_PHONE_FROM="+12345678901"
PHONEBLASTER_DOWNLOAD_TWILIO_ACCOUNT_SID=${PHONEBLASTER_CALL_TWILIO_ACCOUNT_SID}
PHONEBLASTER_DOWNLOAD_TWILIO_AUTH_TOKEN=${PHONEBLASTER_CALL_TWILIO_AUTH_TOKEN}
```

`phoneblaster.py` will now start with default values from your `.env` file.

* [Example .env file](.env.example)

#### Usage

`phoneblaster.py --help`

```
☎️ Phone Blaster
Usage: phoneblaster.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  call
  download
```

`phoneblaster.py call --help`

```
☎️ Phone Blaster
Usage: phoneblaster.py call [OPTIONS]

Options:
  --twilio-account-sid TEXT  Twilio Account SID  [required]
  --twilio-auth-token TEXT   Twilio Auth Token  [required]
  --twilio-phone-from TEXT   Twilio Phone Number to Call From
                             (+12345678901)
  --phone-to TEXT            Phone Number to Call To (+10987654321)
                             [required]
  --twiml-url TEXT           TwiML URL (http)  [required]
  --count INTEGER            Phone Call Count
  --interval INTEGER         Interval Between Calls (seconds)
  --record BOOLEAN           Record Phone Call
  --log-dir TEXT             Call Log Directory
  --help                     Show this message and exit.
```

`phoneblaster.py download --help`

```
☎️ Phone Blaster
Usage: phoneblaster.py download [OPTIONS]

Options:
  --twilio-account-sid TEXT  Twilio Account SID  [required]
  --twilio-auth-token TEXT   Twilio Auth Token  [required]
  --log-dir TEXT             Call Log Directory
  --extension TEXT           Recording Audio File Extension (mp3 or wav)
  --recording-dir TEXT       Recording Directory
  --help                     Show this message and exit.
```

#### Examples

`phoneblaster.py call`

```
☎️ Phone Blaster
Phone Number To (+10987654321): +12345678901
TwiML URL (http) [http://demo.twilio.com/docs/voice.xml]: 
Phone Call Count [1]: 3
Interval Between Calls (seconds) [60]: 10
📁 2022-01-01 00:00:01 Created Directory: logs/
📁 2022-01-01 00:00:01 Created File: logs/12345678901.csv
📞 2022-01-01 00:00:01 Call From: +10987654321 To: +12345678901
✏️ 2022-01-01 00:00:01 Writing Call SID: ABCDEFGHIJKLMNOPQRSTUVWXYZ01234561
⏸ Pausing for 10 seconds
📞 2022-01-01 00:00:11 Call From: +10987654321 To: +12345678901
✏️ 2022-01-01 00:00:11 Writing Call SID: ABCDEFGHIJKLMNOPQRSTUVWXYZ01234562
⏸ Pausing for 10 seconds
📞 2022-01-01 00:00:21 Call From: +10987654321 To: +12345678901
✏️ 2022-01-01 00:00:21 Writing Call SID: ABCDEFGHIJKLMNOPQRSTUVWXYZ01234563
✅ Finished
```

`phoneblaster.py download`

```
☎️ Phone Blaster
📖 2022-01-01 00:01:01 Reading Call Log CSV File: logs/12345678901.csv
📁 2022-01-01 00:01:02 Created Directory: recordings/
📁 2022-01-01 00:01:02 Created Subdirectory: recordings/12345678901
🕸 2022-01-01 00:01:02 Requesting: https://api.twilio.com/2010-04-01/Accounts/ABCDEFGHIJKLMNOPQRSTUVWXYZ01234567/Recordings/ABCDEFGHIJKLMNOPQRSTUVWXYZ01234561.mp3
💿 2022-01-01 00:01:03 Downloaded: recordings/12345678901/ABCDEFGHIJKLMNOPQRSTUVWXYZ01234561.mp3
✏️ 2022-01-01 00:01:03 Call Log Updated SID: ABCDEFGHIJKLMNOPQRSTUVWXYZ01234561
🕸 2022-01-01 00:01:03 Requesting: https://api.twilio.com/2010-04-01/Accounts/ABCDEFGHIJKLMNOPQRSTUVWXYZ01234567/Recordings/ABCDEFGHIJKLMNOPQRSTUVWXYZ01234562.mp3
💿 2022-01-01 00:01:04 Downloaded: recordings/12345678901/ABCDEFGHIJKLMNOPQRSTUVWXYZ01234563.mp3
✏️ 2022-01-01 00:01:04 Call Log Updated SID: ABCDEFGHIJKLMNOPQRSTUVWXYZ01234562
✏️ 2022-01-01 00:01:04 Call Log Updated SID: ABCDEFGHIJKLMNOPQRSTUVWXYZ01234564
✅ Finished
```

#### Custom Actions

Twilio has a custom `.xml` file format called TwiML.

* [TwiML Documentation](https://www.twilio.com/docs/voice/twiml)

The Twilio TwiML `voice.xml` file used as a default in `phoneblaster.py`:

[http://demo.twilio.com/docs/voice.xml](http://demo.twilio.com/docs/voice.xml)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say voice="alice">Thanks for trying our documentation. Enjoy!</Say>
  <Play>http://demo.twilio.com/docs/classic.mp3</Play>
</Response>
```

A custom TwiML `.xml` file can be hosted on your publicly facing webserver and used with `phoneblaster.py` by specifying the URL with the `--twiml-url` option.

Even if you host the `.xml` file on a `https` enabled webserver, pass the `http` URL or else Twilio will emit an application error.

Twilio will follow your webservers `301` permanently moved response from `http` to `https`.

* [TwiML Examples](./twiml/)
  * [default.xml](./twiml/default.xml)
  * [digits.xml](./twiml/digits.xml)
  * [pause.xml](./twiml/pause.xml)

---

© 2022 phoenhome.com

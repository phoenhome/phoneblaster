#!/usr/bin/env python3

import csv
import os
import re
import shutil
from datetime import datetime
from tempfile import NamedTemporaryFile
from time import sleep

import click
import requests
from dotenv import load_dotenv
from twilio.rest import Client


# Call log columns
CALL_LOG_FIELDNAMES = ['twilio_account_sid',
                       'twilio_call_sid',
                       'twilio_start_time',
                       'date',
                       'time',
                       'twilio_phone_from',
                       'phone_to',
                       'answered_by',
                       'duration',
                       'status',
                       'this_call',
                       'total_calls',
                       'twiml_url',
                       'recorded',
                       'downloaded',
                       'recording_url']


# Timestamp string format for CLI output
def utcnow():
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


# Click command group
@click.group()
def phoneblaster():
    group_commands = ['call', 'download']


@phoneblaster.command('call')
@click.option('--twilio-account-sid',
              help='Twilio Account SID',
              required=True)
@click.option('--twilio-auth-token',
              help='Twilio Auth Token',
              required=True)
@click.option('--twilio-phone-from',
              help='Twilio Phone Number to Call From (+12345678901)',
              required=False)
@click.option('--phone-to',
              prompt='Phone Number To (+10987654321)',
              help='Phone Number to Call To (+10987654321)',
              required=True)
@click.option('--twiml-url',
              prompt='TwiML URL (http)',
              help='TwiML URL (http)',
              default='http://demo.twilio.com/docs/voice.xml',
              required=True)
@click.option('--count',
              prompt='Phone Call Count',
              help='Phone Call Count',
              default=1,
              type=int,
              required=False)
@click.option('--interval',
              prompt='Interval Between Calls (seconds)',
              help='Interval Between Calls (seconds)',
              default=60,
              type=int,
              required=False)
@click.option('--record',
              help='Record Phone Call',
              default=True,
              required=False)
@click.option('--log-dir',
              help='Call Log Directory',
              default='logs/',
              required=False)
def call(twilio_account_sid, twilio_auth_token, twilio_phone_from, phone_to, twiml_url, count, interval, record, log_dir):
    # Create call log directory
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print('📁 {} Created Directory: {}'.format(utcnow(), log_dir))

    # Create call log
    call_log_csv = '{}{}.csv'.format(log_dir, phone_to.replace('+', ''))
    if not os.path.isfile(call_log_csv):
        with open(call_log_csv, 'w') as csv_file:
            call_log_writer = csv.DictWriter(csv_file, fieldnames=CALL_LOG_FIELDNAMES)
            call_log_writer.writeheader()
            print('📁 {} Created File: {}'.format(utcnow(), call_log_csv))

    for i in range(count):
        # Initialize Twilio client
        twilio_client = Client(twilio_account_sid, twilio_auth_token)

        # Initiate call
        twilio_call = twilio_client.calls.create(
            record=record,
            url=twiml_url,
            to=phone_to,
            from_=twilio_phone_from)
        twilio_call_sid = twilio_call.sid
        print('📞 {} Call From: {} To: {}'.format(utcnow(), twilio_phone_from, phone_to))

        # Add call to call log
        with open(call_log_csv, 'a') as csv_file:
            call_log_writer = csv.writer(csv_file)
            call_log_row = [twilio_account_sid,                       # twilio_account_sid
                            twilio_call_sid,                          # twilio_call_sid
                            None,                                     # twilio_start_time
                            datetime.utcnow().strftime('%Y-%m-%d'),   # date
                            datetime.utcnow().strftime('%H:%M:%S'),   # time
                            twilio_phone_from,                        # twilio_phone_from
                            phone_to,                                 # phone_to
                            None,                                     # answered_by
                            None,                                     # duration
                            None,                                     # status
                            i + 1,                                    # this_call
                            count,                                    # total_calls
                            twiml_url,                                # twilml_url
                            record,                                   # recorded
                            False,                                    # downloaded
                            None]                                     # recording_url
            call_log_writer.writerow(call_log_row)
            print('✏️ {} Writing Call SID: {}'.format(utcnow(), twilio_call_sid))

        if i < (count - 1):
            print('⏸ Pausing for {} seconds'.format(interval))
            sleep(interval)

    print('✅ Finished')


@phoneblaster.command('download')
@click.option('--twilio-account-sid',
              help='Twilio Account SID',
              required=True)
@click.option('--twilio-auth-token',
              help='Twilio Auth Token',
              required=True)
@click.option('--log-dir',
              help='Call Log Directory',
              default='logs/',
              required=False)
@click.option('--extension',
              help='Recording Audio File Extension (mp3 or wav)',
              default='mp3',
              required=False)
@click.option('--recording-dir',
              help='Recording Directory',
              default='recordings/',
              required=False)
def download(twilio_account_sid, twilio_auth_token, log_dir, extension, recording_dir):
    # Find all call log CSV files
    log_file_regex = re.compile('[\d]*.csv')
    call_log_csv_files = ['{}{}'.format(log_dir, file) for file in os.listdir(log_dir) if log_file_regex.match(file)]

    for call_log_csv in call_log_csv_files:
        # Create call log temp file
        tempfile = NamedTemporaryFile(mode='w', delete=False)

        with open(call_log_csv, 'r') as csv_file:
            # Read from existing call log
            call_log_reader = csv.DictReader(csv_file, fieldnames=CALL_LOG_FIELDNAMES)
            # Write to temp call log
            call_log_writer = csv.DictWriter(tempfile, fieldnames=CALL_LOG_FIELDNAMES)

            print('📖 {} Reading Call Log CSV File: {}'.format(utcnow(), call_log_csv))
            for call_log_row in call_log_reader:
                if call_log_row['downloaded'] == 'False':
                    # Initialize Twilio client
                    twilio_client = Client(twilio_account_sid, twilio_auth_token)

                    # Find call by SID
                    twilio_call_sid = call_log_row['twilio_call_sid']
                    twilio_call = twilio_client.calls(twilio_call_sid)

                    # Request call recording list
                    recordings = twilio_call.recordings.list()
                    for recording in recordings:
                        # Create recording directory
                        if not os.path.exists(recording_dir):
                            os.makedirs(recording_dir)
                            print('📁 {} Created Directory: {}'.format(utcnow(), recording_dir))

                        # Create phone number subdirectory
                        phone_number_subdir = '{}{}'.format(recording_dir, call_log_row['phone_to'].replace('+', ''))
                        if not os.path.exists(phone_number_subdir):
                            os.makedirs(phone_number_subdir)
                            print('📁 {} Created Subdirectory: {}'.format(utcnow(), phone_number_subdir))

                        # Construct audio recording URL
                        recording_path = recording.uri.replace('.json', '.{}'.format(extension))
                        recording_url = 'https://api.twilio.com{}'.format(recording_path)
                        call_log_row['recording_url'] = recording_url

                        # Request audio recording URL
                        print('🕸 {} Requesting: {}'.format(utcnow(), recording_url))
                        request = requests.get(recording_url, allow_redirects=True)

                        # Write audio recording file
                        filename = '{}/{}.{}'.format(phone_number_subdir, twilio_call_sid, extension)
                        with open(filename, 'wb') as file:
                            file.write(request.content)
                            print('💿 {} Downloaded: {}'.format(utcnow(), filename))

                    # Update call log with additional call details from Twilio
                    call_details = twilio_call.fetch()
                    call_log_row['twilio_start_time'] = call_details.start_time
                    call_log_row['answered_by'] = call_details.answered_by
                    call_log_row['duration'] = call_details.duration
                    call_log_row['status'] = call_details.status
                    call_log_row['downloaded'] = True
                    call_log_writer.writerow(call_log_row)
                    print('✏️ {} Call Log Updated SID: {}'.format(utcnow(), call_details.sid))
                else:
                    # Write unchanged call row
                    call_log_writer.writerow(call_log_row)

        # Swap new call log with old call log
        shutil.move(tempfile.name, call_log_csv)

    print('✅ Finished')


if __name__ == '__main__':
    print('☎️ Phone Blaster')
    load_dotenv()
    phoneblaster(auto_envvar_prefix='PHONEBLASTER')

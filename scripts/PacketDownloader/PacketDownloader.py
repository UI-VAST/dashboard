#!/usr/bin/python2

from __future__ import print_function

import httplib2
import oauth2client     # $ pip install google-api-python-client
import os
import base64
import time
import email

from googleapiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client import file
from googleapiclient import errors

UPDATE_INTERVAL = 5        # seconds
NEW_LABEL_ID = None   # Gmail label ID of 'new' label

# command line arguments
try:
    import argparse
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    parser.add_argument('-a', '--all', action='store_true', dest='download_all', default='false', help='Download all attachments (else only download new)')
    parser.add_argument('-l', '--label', required=True, help='Gmail label to use after attachment is downloaded (or label to download attachments from if --all is used)')
    parser.add_argument('-d', '--directory', default='.', help='Specify parent directory in which download directory will be created')
    flags = parser.parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Packet Downloader'

# Gmail authentication
def get_credentials():
#    home_dir = os.path.expanduser('~')
#    credential_dir = os.path.join(home_dir, '.credentials')
    credential_dir = './.credentials'
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'credentials.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

# Gmail advanced search
def ListMessagesMatchingQuery(service, user_id, query=''):
    try:
        response = service.users().messages().list(userId=user_id, q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=query, pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages
    except errors.HttpError, error:
        print('An error occurred: %s' % error)

# Download message body and attachment
def GetData(service, user_id, msg_id, prefix=""):
    sbd_filename = ''
    csv_filename = 'packets.csv'

    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()

        for part in message['payload']['parts']:
            if part['filename']:
                sbd_filename = message['internalDate'] + '.sbd'
                if not sbd_filename is '':
                    if 'data' in part['body']:
                        data=part['body']['data']
                    else:
                        att_id=part['body']['attachmentId']
                        att=service.users().messages().attachments().get(userId=user_id, messageId=msg_id,id=att_id).execute()
                        data=att['data']
                    file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                    sbd_dl_path = os.path.join(prefix, 'sbd', 'new', sbd_filename)
                    csv_dl_path = os.path.join(prefix, csv_filename)

                    if not os.path.exists(sbd_dl_path) and not os.path.exists(os.path.join(prefix, 'sbd', sbd_filename)):
                        #download individual sbd
                        with open(sbd_dl_path, 'w') as f:
                            f.write(file_data)
                            f.close()

                        #append contents to packets.csv
                        with open(csv_dl_path, 'a') as f:
                            f.write(file_data + '\n')
                            f.close()

                        record('Downloaded ' + sbd_dl_path)
                    else:
                        record('Skipped ' + sbd_dl_path)
                    
    except errors.HttpError, error:
        print('An error occurred: %s' % error)

    try:
        if not sbd_filename is '':
            message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
            txt_file = sbd_filename[:-3] + 'txt'
            txt_path = os.path.join(prefix, 'txt', txt_file)

            if message['raw']:
                if not os.path.exists(txt_path):
                    data=message['raw']

                    file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))

                    msg = email.message_from_string(file_data)
                    for part in msg.walk():
                        if part.get_content_type() == 'text/plain':
                            msg_txt = part.get_payload()

                    with open(txt_path, 'w') as f:
                        f.write(msg_txt)
                        f.close()

                    record('Downloaded ' + txt_path)
                else:
                    record('Skipped ' + txt_path)
    except errors.HttpError, error:
        print('An error occurred: %s' % error)

# create label object
def CreateLabel(service, user_id, label_object):
  try:
    label = service.users().labels().create(userId=user_id, body=label_object).execute()
    return label
  except errors.HttpError, error:
    print('An error occurred: %s' % error)

# make actual label in Gmail
def MakeLabel(label_name, mlv='show', llv='labelShow'):
  label = {'messageListVisibility': mlv,
           'name': label_name,
           'labelListVisibility': llv}
  return label

# add/remove labels from email
def ModifyMessage(service, user_id, msg_id, msg_labels):
  try:
    message = service.users().messages().modify(userId=user_id, id=msg_id, body=msg_labels).execute()
                                                
    label_ids = message['labelIds']

    return message
  except errors.HttpError, error:
    print('An error occurred: %s' % error)

# set which labels to add/remove
def CreateMsgLabels(new_label_id, label_id):
    return {'removeLabelIds': [new_label_id], 'addLabelIds': [label_id]}

# use to find label ID of 'new' label (only used on initial run for each new Gmail account)
def ListLabels(service, user_id):
  try:
    response = service.users().labels().list(userId=user_id).execute()
    labels = response['labels']
    return labels
  except errors.HttpError, error:
    print('An error occurred: %s' % error)

# log data and print to screen
def record(text):
    localtime = time.asctime(time.localtime(time.time()))
    log_path = os.path.join(flags.directory, flags.label, 'log.txt')
    with open(log_path, 'a') as log:
        log.write(localtime + '\t' + text + '\n')
        log.close()
    print(localtime + '\t' + text)

def main():
	# Gmail authentication
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    check = True
    label_exists = False

    # retrieve list of Gmail labels
    labels = ListLabels(service, 'me')

    for label in labels:
        # check if specified label exists
        if label['name'] == flags.label:
            label_id = label['id']
            label_exists = True
        # get label_ID of 'new' label
        elif label['name'] == 'new':
            NEW_LABEL_ID = label['id']
    
    if flags.directory is '.':
        dir_path = os.path.join(os.getcwd(), flags.label)
    else:
        dir_path = os.path.join(flags.directory, flags.label)

    # check if directory/logfile must be created
    if label_exists is True or flags.download_all == 'false':
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            record('Created directory ' + dir_path)

            log_path = os.path.join(dir_path, 'log.txt')
            if not os.path.exists(log_path):
                open(log_path, 'w').close()

            sbd_path = os.path.join(dir_path, 'sbd')
            if not os.path.exists(sbd_path):
                os.makedirs(sbd_path)
                record('Created directory ' + sbd_path)
            
            sbd_dl_path = os.path.join(sbd_path, 'new')
            if not os.path.exists(sbd_dl_path):
                os.makedirs(sbd_dl_path)
                record('Created directory ' + sbd_dl_path)

            txt_path = os.path.join(dir_path, 'txt')
            if not os.path.exists(txt_path):
                os.makedirs(txt_path)
                record('Created directory ' + txt_path)

    while check is True:

	# download all packets with specified label
        if flags.download_all is True:
            if label_exists is True:
                messages = ListMessagesMatchingQuery(service,'me', 'label:' + flags.label)
                if not messages:
                    record('No messages found.')

                else:
                    for message in messages:
                        GetData(service, 'me', message['id'], dir_path)
            else:
                localtime = time.asctime(time.localtime(time.time()))
                print(localtime + '\tLabel \'' + flags.label + '\' does not exist.')
                check = False

	# download all new packets and relabel with specified label
        else:
            messages = ListMessagesMatchingQuery(service,'me', 'label:new')

            if not messages:
                record('No messages found.')
            else:
                if label_exists is False:
                    record('Creating label ' + flags.label)
                    label_object = MakeLabel(flags.label, mlv='show', llv='labelShow')
                    label = CreateLabel(service, 'me', label_object)
                    label_id = label['id']
		    label_exists = True

                for message in messages:
                    GetData(service, 'me', message['id'], dir_path)
                    msg_label = CreateMsgLabels(NEW_LABEL_ID, label_id)
                    ModifyMessage(service, 'me', message['id'], msg_label)

        if check is True:
            time.sleep(UPDATE_INTERVAL)

if __name__ == '__main__':
    main()

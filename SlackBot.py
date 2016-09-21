"""
SlackBot is a module containing the SlackBotInterface,
from which responsive Slack bots can inherit.

Copyright (c) 2016 Donald E. Willcox

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import time
import re
import os
import requests
from slackclient import SlackClient

class SlackBotInterface(SlackClient):
    def __init__(self, bot_id_file, watch_only):
        # Bot identity and token
        self.identity = ''
        self.token    = ''

        # Get Bot ID and Token from bot_id_file
        self.read_token_from_file(bot_id_file)

        # Initialize parent class
        super(SlackBotInterface, self).__init__(self.token)
        
        # Bot ID tag expression
        self.tag      = '<@{}>'.format(self.identity)
        
        # Bot authentication header for downloading files using requests
        self.request_headers = {'Authorization': 'Bearer {}'.format(self.token)}

        # Instructions are alphanumeric with underscores but no other characters are allowed, including spaces
        self.re_instruction = self.tag + '\s*(\w*)' # The RE is '[self.tag][unicode whitespace][unicode word]'

        # Dict mapping instructions (keys) to functions (values)
        self.instruction_set = {}

        # Message buffer
        self.message_buffer = []

        # Slack polling delay in seconds
        self.poll_delay = 1

        # Watch only
        self.watch_only = watch_only

    def read_token_from_file(self, file_path):
        # Reads the Bot ID and Token from the file specified in file_path (absolute)
        # Exits with an error if the file isn't supplied or found or the ID and Token aren't present

        # RE for Bot ID: SLACKBOT_ID = [ID] # COMMENT
        re_id_text = r"(\s*)SLACKBOT_ID(\s*)=(\s*)([a-zA-Z0-9_-]*)(\s*)#?.*"
        re_id = re.compile(re_id_text)

        # RE for Bot TOKEN: SLACKBOT_TOKEN = [TOKEN] # COMMENT
        re_token_text = r"(\s*)SLACKBOT_TOKEN(\s*)=(\s*)([a-zA-Z0-9_-]*)(\s*)#?.*"
        re_token = re.compile(re_token_text)

        try:
            fid = open(file_path, 'r')
        except:
            print('Could not open file: {}'.format(file_path))
            exit()

        found_id = False
        found_token = False
        for l in fid:
            match_id = re_id.match(l)
            if match_id:
                self.identity = match_id.group(4)
                found_id = True
            match_token = re_token.match(l)
            if match_token:
                self.token = match_token.group(4)
                found_token = True
            if found_id and found_token:
                break
        fid.close()
        if not (found_id and found_token):
            print('Could not find both ID and Token in file: {}'.format(file_path))
            print('Please supply a file with ID and Token entries on lines matching the following regular expressions:')
            print(re_id_text)
            print(re_token_text)
            exit()

    def lookup_user_name(self, userid):
        # Looks up user name from user id, return None if not found or error
        self.users_list = self.api_call("users.list")
        if self.users_list.get('ok'):
            members = self.users_list.get('members')
            for member in members:
                username = member.get('name')
                id = member.get('id')
                if id == userid:
                    return username
            return None
        else:
            return None

    def get_message_user_tag(self, tagged_message):
        # Returns the user tag for the user who posted tagged_message
        # Get the user to reply to
        reply_user_id = None
        if 'user' in tagged_message:
            reply_user_id = tagged_message['user']
        # Tag the user
        reply_user_tag = ''
        if reply_user_id:
            reply_user_tag = '<@{}>'.format(self.lookup_user_name(reply_user_id))
        return reply_user_tag

    def get_message_text(self, tagged_message):
        # Returns the text of the message, an empty string if not present.
        tagged_text = ''
        if 'text' in tagged_message:
            tagged_text = tagged_message['text']
        return tagged_text

    def get_message_file_url(self, tagged_message):
        # Returns the file URL if there is a file with url_private in the message
        # Otherwise, returns an empty string
        file_url = ''
        if 'file' in tagged_message:
            file_url = tagged_message['file']['url_private']
        return file_url

    def download_file_content(self, file_url):
        # Returns the text of a downloaded file's contents, given its URL
        # NEED TO SANITIZE file_url to prevent sending bot token to non-slack URL's
        r = requests.get(file_url, headers=self.request_headers)
        return r.content.decode()
    
    def ins_confused(self, tagged_message):
        # Formulate a confused reply
        reply = "Help! I don't know what to do"
        return reply

    def execute_instruction(self, instruction, tagged_message):
        # Execute the instruction on this message
        if instruction in self.instruction_set:
            return self.instruction_set[instruction](tagged_message)
        else:
            # If user supplied an instruction I don't recognize, call ins_confused()
            return self.ins_confused(tagged_message)

    def reply_tagged_message(self, tagged_message):
        # Given a message which tags Artoo, interpret it, execute action and reply
        
        # Find which channel the message was posted in for a reply
        reply_channel = None
        if 'channel' in tagged_message:
            reply_channel = tagged_message['channel']

        # Get the text of the message
        tagged_text = None
        if 'text' in tagged_message:
            tagged_text = tagged_message['text']

        # Extract Bot instruction from message
        # Sanity
        if not tagged_text:
            return
        
        # If there is more than one tag to Bot, just extract the first instruction
        instruction = None
        re_match = re.search(self.re_instruction, tagged_text)
        if re_match and re_match.group(1):
            instruction = re_match.group(1)
            
        # Execute instruction given the tagged message
        reply_text = self.execute_instruction(instruction, tagged_message)

        # Post response to the originating channel        
        self.api_call("chat.postMessage", channel=reply_channel, text=reply_text, as_user=True)
    
    def filter_tagged_messages(self):
        # Filter the messages in self.message_buffer to determine who they are for.
        # Return immediately unless a message is directed at the Bot
        # Call self.reply_tagged_message() if a message is directed at the Bot

        if self.watch_only:
            # Just print each message you see if --watch is supplied as an argument.
            for message in self.message_buffer:
                print('----------------------')
                for k in message.keys():
                    print('{}: {}'.format(k, message[k]))
        else:
            for message in self.message_buffer:
                if 'text' in message.keys():
                    # Message has a text field
                    if re.search(self.tag, message['text']):
                        # Message tags Bot, so interpret it.
                        self.reply_tagged_message(message)

    def poll_slack(self):
        if self.rtm_connect():
            print("Successfully logged onto Slack!")
            while True:
                # Poll Slack for new messages and fill buffer
                self.message_buffer = self.rtm_read()
                # Filter and Reply to new messages
                self.filter_tagged_messages()
                time.sleep(self.poll_delay)
        else:
            print("Could not successfully log onto Slack :(")        

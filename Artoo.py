"""
Artoo is a class that interfaces with Slack as a bot user.

To drive Artoo, run 'artoo_driver.py'

Artoo is capable of running python 3 code posted on Slack
within the ```-demarked code tag or within Code Snippets.

On Slack, you can get a description of how to use Artoo
by posting '@artoo help'.

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

import os
import re
from subprocess import Popen, PIPE, TimeoutExpired
from tempfile import NamedTemporaryFile
from SlackBot import SlackBotInterface
            
class Artoo(SlackBotInterface):
    def __init__(self, bot_id_file, watch_only):
        # Initialize the SlackBotInterface
        super(Artoo, self).__init__(bot_id_file, watch_only)

        # Add Artoo's instructions to the instruction set
        self.instruction_set['help'] = self.ins_only_hope
        self.instruction_set['python'] = self.ins_run_python

        # Timeout for running python programs
        self.PY_TIMEOUT_SECS = 300 # 5 minutes

    def run_python_file(self, fname):
        proc = Popen(['python',fname], stdout=PIPE, stderr=PIPE)
        try:
            out, err = proc.communicate(timeout=self.PY_TIMEOUT_SECS)
            exitcode = proc.returncode
        except TimeoutExpired:
            proc.kill()
            out, err = proc.communicate()
            exitcode = 'Artoo halted execution after {} seconds'.format(self.PY_TIMEOUT_SECS)

        # Tell the console what we did.
        # print('code:')
        # print(code)
        # print('out:')
        # print(out.decode())
        # print('err:')
        # print(err.decode())
        # print('return code:')
        # print(exitcode)

        # delete temp file
        print('Deleting temp file: {}'.format(fname))
        os.remove(fname)
        return out.decode(), err.decode(), exitcode

    def run_python(self, code):
        # Execute code as python code using a temporary file and a spawned process.
        ftemp = NamedTemporaryFile(mode='w', delete=False)
        ftemp.write(code)
        ftemp.close()
        print('Executing python in temp file: {}'.format(ftemp.name))
        out, err, exitcode = self.run_python_file(ftemp.name)
        return out, err, exitcode

    def get_code_from_regions(self, base_text):
        # Gets code from code regions denoted by ``` (open) and ``` (close)
        code_extract = ''
        code_denote = '```'
        code_indices = []
        for re_match in re.finditer(code_denote, base_text):
            code_indices.append(re_match.start())
        if len(code_indices)==0:
            code_extract = None
        elif len(code_indices) % 2 == 1:
            code_extract = '!ODD'
        else:
            npairs = int(len(code_indices)/2)
            for j in range(npairs):
                idx_end = code_indices.pop() 
                idx_begin = code_indices.pop() + len(code_denote)
                code_snippet = base_text[idx_begin:idx_end]
                code_extract = code_snippet + '\n' + code_extract
        return code_extract

    def ins_confused(self, tagged_message):
        # Get the reply user tag
        reply_user_tag = self.get_message_user_tag(tagged_message)
        # Formulate a confused reply
        reply = "{} [Confused Electronic Noise]\n--Please provide a command as--\n@artoo python\n```\n[PYTHON 3 CODE]\n```\n--or--\nComment '@artoo python' on a python 3 code snippet.".format(reply_user_tag)
        return reply

    def ins_only_hope(self, tagged_message):
        # Get the user reply tag
        reply_user_tag = self.get_message_user_tag(tagged_message)
        # Reply to user with a help string
        reply = "{} [Electronic Trilling]\n--Please provide a command as--\n@artoo python\n```\n[PYTHON 3 CODE]\n```\n--or--\nComment '@artoo python' on a python 3 code snippet.".format(reply_user_tag)
        return reply
    
    def ins_run_python(self, tagged_message):
        # Get the reply user tag
        reply_user_tag = self.get_message_user_tag(tagged_message)
        
        # Determine if there is a file to run or if there are code block(s)
        file_url = self.get_message_file_url(tagged_message)
        confused = False
        if file_url:
            # Download and run a file if supplied in file_url
            code_to_run = self.download_file_content(file_url)
            if code_to_run == None:
                confused = True
        else:
            # If no file supplied, interpret the code region(s) in this text as python code
            tagged_text = self.get_message_text(tagged_message)
            code_to_run = self.get_code_from_regions(tagged_text)
            if code_to_run == None or code_to_run=='!ODD':
                confused = True
        if not confused:
            out, err, retcode = self.run_python(code_to_run)
            file_tag = ''
            if file_url:
                file_tag = 'File: {}\n'.format(file_url)
            reply = "{} [Beep, Beep, Bleep!]\n{}stdout: {}\nstderr: {}\nreturn code: {}".format(reply_user_tag, file_tag, out, err, retcode)
            return reply
        else:
            return self.ins_confused(tagged_message)

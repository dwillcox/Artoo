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
    def __init__(self, bot_id_file, watch_only, verbose):
        # Initialize the SlackBotInterface
        super(Artoo, self).__init__(bot_id_file, watch_only)

        # Add Artoo's instructions to the instruction set
        self.instruction_set['help'] = self.ins_only_hope
        self.instruction_set['bash'] = self.ins_run_bash
        self.instruction_set['python'] = self.ins_run_python

        # Timeout for running external processes
        self.PROC_TIMEOUT_SECS = 300 # 5 minutes

        # Verbose status
        self.verbose = verbose

    def print_wrapper(self, to_print):
        # Wrapper for python print that checks verbosity status
        if self.verbose:
            print(to_print)

    def open_process(self, program_list):
        # Opens a subprocess using Popen
        # Popen is passed program_list to run
        # Return STDOUT, STDERR, and EXITCODE
        proc = Popen(program_list, stdout=PIPE, stderr=PIPE)
        try:
            out, err = proc.communicate(timeout=self.PROC_TIMEOUT_SECS)
            exitcode = proc.returncode
        except TimeoutExpired:
            proc.kill()
            out, err = proc.communicate()
            exitcode = 'Halted execution after {} seconds'.format(self.PROC_TIMEOUT_SECS)
        return out.decode(), err.decode(), exitcode
    
    def write_to_temp(self, content):
        # Write content to a NamedTemporaryFile and return the file handle
        ftemp = NamedTemporaryFile(mode='w', delete=False)
        ftemp.write(content)
        ftemp.close()
        return ftemp

    def delete_temp(self, temp_handle):
        # Delete the NamedTemporaryFile with handle temp_handle
        self.print_wrapper('Deleting file: {}'.format(temp_handle.name))
        os.remove(temp_handle.name)
    
    def run_bash(self, code):
        # Execute code as bash code using a temporary file and a spawned process.
        ftemp = self.write_to_temp(code)
        self.print_wrapper('Executing bash code in temp file: {}'.format(ftemp.name))
        out, err, exitcode = self.open_process(['bash', ftemp.name])
        # Delete temporary file
        self.delete_temp(ftemp)
        return out, err, exitcode

    def run_python(self, code):
        # Execute code as python code using a temporary file and a spawned process.
        ftemp = self.write_to_temp(code)
        self.print_wrapper('Executing python code in temp file: {}'.format(ftemp.name))
        out, err, exitcode = self.open_process(['python', ftemp.name])
        # Delete temporary file
        self.delete_temp(ftemp)
        return out, err, exitcode

    def ins_confused(self, tagged_message):
        # Help!
        reply = self.ins_only_hope(tagged_message)
        return reply

    def ins_only_hope(self, tagged_message):
        # Get the user reply tag
        reply_user_tag = self.get_message_user_tag(tagged_message)
        # Reply to user with a help string
        reply = "{} [Electronic Trilling]\n--Please provide a command as--\n@artoo bash\n```\n[BASH CODE]\n```\n--or--\n@artoo python\n```\n[PYTHON 3 CODE]\n```\n--or--\nComment '@artoo python' or '@artoo bash' on a code snippet.".format(reply_user_tag)
        return reply

    def ins_run_bash(self, tagged_message):
        # Get the reply user tag
        reply_user_tag = self.get_message_user_tag(tagged_message)
        
        # Get the message code
        message_code, file_url = self.get_message_code(tagged_message)

        # Run code with bash and formulate reply
        if message_code:
            self.print_wrapper('bash code:')
            self.print_wrapper(message_code)
            out, err, retcode = self.run_bash(message_code)
            file_tag = ''
            if file_url:
                file_tag = 'File: {}\n'.format(file_url)
            reply = "{} [Beep, Beep, Bleep!]\n{}stdout:\n{}\nstderr:\n{}\nreturn code: {}".format(reply_user_tag, file_tag, out, err, retcode)
            return reply
        else:
            return self.ins_confused(tagged_message)

    def ins_run_python(self, tagged_message):
        # Get the reply user tag
        reply_user_tag = self.get_message_user_tag(tagged_message)
        
        # Get the message code
        message_code, file_url = self.get_message_code(tagged_message)

        # Run code with python and formulate reply
        if message_code:
            self.print_wrapper('python code:')
            self.print_wrapper(message_code)
            out, err, retcode = self.run_python(message_code)
            file_tag = ''
            if file_url:
                file_tag = 'File: {}\n'.format(file_url)
            reply = "{} [Beep, Beep, Bleep!]\n{}stdout:\n{}\nstderr:\n{}\nreturn code: {}".format(reply_user_tag, file_tag, out, err, retcode)
            return reply
        else:
            return self.ins_confused(tagged_message)

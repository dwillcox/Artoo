"""
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

# Artoo Driver
import argparse
from Artoo import Artoo

parser = argparse.ArgumentParser()
parser.add_argument('idfile', type=str, help='Bot identity file from which to read the Bot ID and Token.')
parser.add_argument('-watch', '--watch', action='store_true', help='Watch all slack messages and print them to the console.')
parser.add_argument('-v', '--verbose', action='store_true', help='Print an activity log to console.')
args = parser.parse_args()

artoo = Artoo(args.idfile, args.watch, args.verbose)
artoo.poll_slack()

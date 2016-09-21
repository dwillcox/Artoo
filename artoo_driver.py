# Artoo Driver
import argparse
from Artoo import Artoo

parser = argparse.ArgumentParser()
parser.add_argument('-idfile', '--identityfile', type=str, help='Bot identity file from which to read the Bot ID and Token.')
parser.add_argument('-watch', '--watch', action='store_true', help='Watch all slack messages and print them to the console.')
args = parser.parse_args()

artoo = Artoo(args.identityfile, args.watch)
artoo.poll_slack()

# Artoo

Code Evaluation Slack Bot

## Set up ID and Token

Create a file to store the ID and Token for the bot, e.g. '.artoo'

The program looks for your bot ID and Token on lines of the file as follows:

```
SLACKBOT_ID = [Your Bot ID]
SLACKBOT_TOKEN = [Your Bot Token]

```

## Running

To run Artoo using the '.artoo' file in the above step, simply do:

```
$ python artoo_driver.py -idfile .artoo

```

## Watching

You can set Artoo to 'watch only' and Artoo will print all Slack
messages it finds to the console, regardless whether or not Artoo is
tagged in them. Artoo will not post to Slack in this mode, but it's
useful for developing.

```
$ python artoo_driver.py -idfile .artoo -watch

```


# Bot for Server Monitoring - by Landomix

## Index
- [Purpose](#purpose)
- [How it works](#how-it-works)
- [Setup](#setup)
    - [Env file - Creation](#env-file---creation)
    - [Telegram Bot](#telegram-bot)
    - [Filling the Env file](#filling-the-env-file)
    - [Python Environment, code download and run.](#python-environment-code-download-and-run)
- [Privacy disclaimer](#privacy-disclaimer)

## Purpose
This bot is intended to be used for the setup of the servers in the Lab in which I'm doing the thesis. **It is ment to work only there, no guarantees in other settings** (**Pull Requests for improvements are welcome**!). It alerts you when a process of yours exit
the GPU (when it doesn't appear anymore in `nvidia-smi`'s output: I'm assuming it exits when your run stops), and warns when available space is less than a threshold. **N.B.: Unfortunately I cannot Upload directly the poetry.lock file**, since different servers has different python versions. I modified the toml file, keep in mind that is working (tested) with python `3.8` and `3.11.6` (we can safely assume that also versions in the middle works).

**THIS BOT IS IN BETA**: no guarantees. Pull Requests for improvements are welcome!

## How it works:
Every minute the bot checks if you're running processes on the GPU, alerts you when they exit the GPU, and alerts you if the free space on the disk decreases under a certain threshold **while** you are running things. If space decreases due to other people's usage of the server, and you're running nothing on the GPU, you won't be alerted. Alerts will continue every minute, and this will let you time for free up space before everything crashes.

You will receive also a notification when your run has finished (assuming that the run finishes when the process is no more listed in the output of `nvidia-smi`)

Since when running `nvidia-smi`, you can see the path to the python interpreter running, and since the path involves your home (hence in the path will appear your username), by doing a grep and count the number of appearence of your username, you know how many processes you are running (don't name other folders with your username string, otherwise this is no more true).

**Multi Process needs to be tested, help is wanted**.

## Setup
### Env file - Creation
Everything is set up by environment variables.
Assuming your shell is bash (on the servers of my lab it is so), what you can do is for example create a file in your home, named
`.bot_environment_variables` (without extension, it is ok), and add the following line to your ~/.bashrc file:
```
source /home/<USERNAME>/.bot_environment_variables
```
where `<USERNAME>` needs to be replaced with your username in the server.

After this, type in terminal:
```
$ source .bashrc
```
### Telegram Bot
Now you need to create a telegram bot: follow the instructions [here](https://core.telegram.org/bots/tutorial#obtain-your-bot-token), and save the token somewhere, you will need to insert it later in a specific position in the file you created (`~/.bot_environment_variables`).

After this, you need to detect your chat ID: on your browser, go to: `https://api.telegram.org/bot<TOKEN>/getUpdates`, where instead of `<TOKEN>`
you need to place the token of the bot generated through botfather. Send a message from telegram (e.g., from your phone's app) to your bot, and refresh the page on the browser: you should see that a message appeared in the JSON, and search for the field `id` in the `chat` section. That's your chat id, take note of it, it will be needed to fill the environment variables file

### Filling the Env file
Open with your favourite editor the file `~/.bot_environment_variables`, and fill it. It content needs to be:

```
export BOT=<TOKEN>
export CHAT_ID=<ID>
export GB_ALERT=<NMBR>
export USERNAME_TO_CHECK='<USERNAME>'
```
Where:
- `<TOKEN>` is the token of the bot, given when you created it.
- `<ID>` is your personal chat id detected from the json in the browser (messages will be sent to that chat id).
- `<NMBR>` is the number of free GB under which you want to be alerted if you're running code (e.g., if `<NMBR>` is $5$, you will receiv alerts when less than $5$ GB are available).
- `<USERNAME>` is your username.

### Python Environment, code download and run.
Create a new virtual environment for this bot. Assuming that as on my server you have your original python environment in `$ venv/`, activate it with:
```
source $HOME/venv/bin/activate 
```
and create a new one (with the following command you will have a new environment named `monitoring` in your home):
```
python -m venv $HOME/monitoring
```
Deactivate the previous one, and activate monitoring:
```
deactivate && source $HOME/monitoring/bin/activate
```
Install poetry:
```
pip install poetry
```
cd into the folder of this project
```
cd /path/to/folder/visionlab-monitoring/ && poetry install --no-root
```
Still in the repo folder, run the file `bot.py`

## Run and Usage
You should run this in a `screen` session, and detach from it: until the server reboots, it will be running.

## Privacy Disclaimer
Sudoers of the server will be able to see your bot token and your chat id, since they will be able to access your environment file.

**Sudoers**: your students trust you ;)
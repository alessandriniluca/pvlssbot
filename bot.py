import os
from time import sleep
from telegram import Update
from telegram.ext import *
import psutil
import asyncio
import subprocess

debug = False
global_count = 0

def get_disk_usage(path) -> float:
    """Check the remaining space in the path specified

    Args:
        path (str): Path for which check remaining space. For my lab, this should be set to "/" 

    Returns:
        float: Remaining GB
    """
    if debug:
        print(f'[DEBUG]: Checking {path}')
    disk_usage = psutil.disk_usage(path)
    available_space_gb = disk_usage.free / (2**30) # Convert bytes to gigabytes
    if debug:
        print(f'[DEBUG]: Available space for {path}: {available_space_gb} GB. Plese check it with command \'df -h\'')
    return available_space_gb

def check_username_running(username):
    """Chekcs how many times your username appears when running "nvidia-smi". Do not name folders with your username,
    as it will check for the username in the string leading to the python interpreter you're using

    Args:
        username (str): username for which to check, e.g., lucaa97

    Returns:
        int: number of processes running
    """
    command = f"nvidia-smi | grep {username} | wc -l"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    return int(output.decode().strip())

async def monitor_server(application):
    """Monitoring the server, this is the main thing running performing all the checks

    Args:
        application (telegram.ext._application.Application): Telegram Application
    """
    global debug
    global global_count
    path = "/"

    username_to_check = os.environ.get('USERNAME_TO_CHECK')
    await application.bot.send_message(chat_id=os.environ.get('CHAT_ID'), text="Your bot has been (re-)started!")
    # every minute check if something is running
    while True:
        # check if there are processes running
        process_count = check_username_running(username_to_check)

        # if the counter is less than the global counter, send a message since one has finished,
        #     alert that one process finished, print remaining ones, and print remaining space.
        #     update global counter
        if process_count < global_count:
            free_gb = get_disk_usage(path)
            await application.bot.send_message(chat_id=os.environ.get('CHAT_ID'), text=f"Your run has finished, available space: {free_gb:.2f} GB. Still running processes: {process_count}")
            global_count = process_count
        elif process_count > global_count:
            # elseif counter greater than global counter, then alert that one process started, send disk space,
            #     update global counter
            free_gb = get_disk_usage(path)
            await application.bot.send_message(chat_id=os.environ.get('CHAT_ID'), text=f"Your run has started, available space: {free_gb:.2f} GB. Running processes: {process_count}")
            global_count = process_count
        # elseif global count greater than zero, then we need to monitor disk space. -> global counter neither increased nor decreased
        elif global_count > 0:
            free_gb = get_disk_usage(path)
            if free_gb < int(os.environ.get('GB_ALERT')):
                await application.bot.send_message(chat_id=os.environ.get('CHAT_ID'), text="Your disk space is running low! Only {:.2f} GB left.".format(free_gb))
        # sleep one minute
        await asyncio.sleep(60)



if __name__ == '__main__':
    print("[pvlssbot]: You started pvlssbot, powered by")
    print("██╗░░░░░░█████╗░███╗░░██╗██████╗░░█████╗░███╗░░░███╗██╗██╗░░██╗")
    print("██║░░░░░██╔══██╗████╗░██║██╔══██╗██╔══██╗████╗░████║██║╚██╗██╔╝")
    print("██║░░░░░███████║██╔██╗██║██║░░██║██║░░██║██╔████╔██║██║░╚███╔╝░")
    print("██║░░░░░██╔══██║██║╚████║██║░░██║██║░░██║██║╚██╔╝██║██║░██╔██╗░")
    print("███████╗██║░░██║██║░╚███║██████╔╝╚█████╔╝██║░╚═╝░██║██║██╔╝╚██╗")
    print("╚══════╝╚═╝░░╚═╝╚═╝░░╚══╝╚═════╝░░╚════╝░╚═╝░░░░░╚═╝╚═╝╚═╝░░╚═╝")
    print("N.B.: this bot is in beta, no guarantees. Pull Requests for improvement are welcome!")
    application = Application.builder().token(os.environ.get('BOT')).build()

    # Add the handler
    application.add_handler(MessageHandler(filters.Command, monitor_server))

    # Run the bot
    loop = asyncio.get_event_loop()
    loop.create_task(monitor_server(application))
    application.run_polling(1.0)
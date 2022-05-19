from functools import reduce

from telegram import Update
from telegram.ext import CallbackContext

import config
from database import Database
from storage import Storage


class Users:

    @staticmethod
    def add(update: Update, context: CallbackContext):
        try:
            username = context.args[0]
            if username not in Storage().users:
                Storage().users.append(username)
                Database().dump()
                update.message.reply_markdown_v2(
                    f"*[INFO]*\nUsername @{username} is added successfully")
            else:
                update.message.reply_markdown_v2(
                    f"*[INFO]*\nUsername @{username} exists")
        except Exception as e:
            if config.DEBUG:
                update.message.reply_text(f"[ERROR]\nadd_user\nException: {e}")

    @staticmethod
    def remove(update: Update, context: CallbackContext):
        try:
            username = context.args[0]
            if username in Storage().users:
                Storage().users.remove(username)
                Database().dump()
                update.message.reply_markdown_v2(
                    f"*[INFO]*\nUsername @{username} is removed successfully")
            else:
                update.message.reply_markdown_v2(
                    f"*[INFO]*\nUsername @{username} does not exist")
        except Exception as e:
            if config.DEBUG:
                update.message.reply_text(
                    f"[ERROR]\nremove_user\nException: {e}")

    @staticmethod
    def list(update: Update, _: CallbackContext):
        if update.effective_user.username in config.USER_WHITELIST:
            users = reduce(lambda x, y: f'{x}\n@{y}', Storage().users, '')
            message = '[NO USER]' if users == '' else f"*[INFO]*\n{users}"
            update.message.reply_markdown_v2(message)

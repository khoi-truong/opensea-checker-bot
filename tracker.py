import logging
from typing import List, Optional

from telegram import Update
from telegram.ext import CallbackContext

import config
import validation
from asset import AssetIdentifier
from asset_requests import get_asset, get_created_event
from chat import ChatInfo
from database import Database
from messenger import Messenger
from poller import AssetPoller
from storage import Storage


class AssetTracker:

    @classmethod
    def track(cls, update: Update, context: CallbackContext):
        """Track an NFT address on OpenSea"""
        try:
            cls.__verify_user(update.effective_user.username)
            asset_identifier = cls.__get_identifier(context.args)
            cls.__track_asset(identifier=asset_identifier, update=update)
        except validation.ValidationError as validation_error:
            update.message.reply_markdown_v2(validation_error.message)
        except Exception as error:
            if config.DEBUG:
                update.message.reply_text(
                    f"[ERROR]\ntrack\nException: {error}")

    @classmethod
    def untrack(cls, update: Update, context: CallbackContext):
        """Untrack an NFT address on OpenSea"""
        try:
            cls.__verify_user(update.effective_user.username)
            asset_identifier = cls.__get_identifier(context.args)
            cls.__untrack_asset(identifier=asset_identifier, update=update)
        except validation.ValidationError as validation_error:
            update.message.reply_markdown_v2(validation_error.message)
        except Exception as error:
            if config.DEBUG:
                update.message.reply_text(
                    f"[ERROR]\nuntrack\nException: {error}")

    @classmethod
    def list(cls, update: Update, _: CallbackContext):
        """List all NFT addresses that are being tracked."""
        try:
            username = update.effective_user.username
            cls.__verify_user(username)
            assets = ''
            for key, chat in Storage().asset_chats.items():
                if chat.username.lower() == username.lower():
                    asset = Storage().get_asset(key)
                    if asset is not None:
                        assets += f"""📦 <a href="{asset.url}">{asset.name}</a>\n\n"""
                    else:
                        assets += f"🔑 {key}\n"
            assets.removesuffix("\n\n")
            message = '<b>EMPTY</b>' if assets == '' else f"<b>TRACKING ASSETS</b>\n\n{assets}"
            update.message.reply_html(message)
        except validation.ValidationError as validation_error:
            update.message.reply_markdown_v2(validation_error.message)
        except Exception as error:
            logging.error('Failed.', exc_info=error)
            if config.DEBUG:
                update.message.reply_text(f"[ERROR]\nlist\nException: {error}")

    @classmethod
    def __track_asset(cls, identifier: AssetIdentifier, update: Update):
        if identifier.to_str() in Storage().asset_chats.keys():
            raise validation.EXISTED_IN_TRACKING_LIST_ERROR
        asset = get_asset(identifier)
        username = update.effective_user.username
        chat = ChatInfo(chat=update.effective_chat, username=username)
        messenger = Messenger(bot=update.message.bot, chat=chat)
        if asset is None:
            messenger.notify_not_found_asset(identifier=identifier)
        else:
            event = get_created_event(identifier)
            if event is None:
                messenger.notify_not_created_asset(asset=asset)
            else:
                messenger.notify_created_asset(asset=asset)
                return
        Storage().set_chat(key=identifier.to_str(), chat=chat)
        if asset is not None:
            Storage().set_asset(key=identifier.to_str(), asset=asset)
        Database().dump()
        AssetPoller().start_polling_asset(identifier, asset)

    @classmethod
    def __untrack_asset(cls, identifier: AssetIdentifier, update: Update):
        key = identifier.to_str()
        if key not in Storage().asset_chats.keys():
            update.message.reply_markdown_v2(
                f"*[INFO]*\nThe asset is not being tracked yet\n{key}")
            return
        AssetPoller.stop_polling_asset(identifier)
        Storage().pop_chat(key)
        Storage().pop_asset(key)
        Database().dump()
        update.message.reply_markdown_v2(
            f"*[INFO]*\nUntrack successfully\n{key}")

    @classmethod
    def __verify_user(cls, username: str):
        stored_users = Storage().users
        usernames = config.USER_WHITELIST + stored_users
        if username.lower() not in map(lambda x: x.lower(), usernames):
            raise validation.NOT_IN_WHITELIST_ERROR

    @classmethod
    def __get_identifier(cls, args: Optional[List[str]]) -> AssetIdentifier:
        if not args:
            raise validation.COMMAND_SYNTAX_ERROR
        if not args[0].startswith('0x'):
            raise validation.ADDRESS_SYNTAX_ERROR
        if len(args) == 1:
            if args[0].find('/') != -1:
                split_args = args[0].split('/')
                asset_contract_address = split_args[0]
                token_id = split_args[1]
            else:
                raise validation.COMMAND_SYNTAX_ERROR
        elif len(args) == 2:
            asset_contract_address = args[0]
            token_id = args[1]
        else:
            raise validation.COMMAND_SYNTAX_ERROR
        try:
            int(token_id)
        except ValueError as value_error:
            raise validation.TOKEN_ERROR from value_error
        if len(asset_contract_address) <= 2:
            raise validation.ADDRESS_LENGTH_ERROR
        return AssetIdentifier(contract_address=asset_contract_address, token_id=token_id)

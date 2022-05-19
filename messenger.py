from copy import deepcopy

from telegram import Bot, ParseMode
import telegram

import config
from asset import Asset, AssetIdentifier
from chat import ChatInfo


class Messenger:
    bot: Bot
    chat: ChatInfo

    def __init__(self, bot: Bot, chat: ChatInfo):
        self.bot = bot
        self.chat = deepcopy(chat)

    def __send_photo_or_message(self, photo, caption: str):
        if not photo:
            self.bot.send_message(
                chat_id=self.chat.id,
                text=caption,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
        else:
            text = f"""<a href='{photo}'>&#8205;</a>""" + caption
            self.bot.send_message(
                chat_id=self.chat.id,
                text=text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False
            )

    def notify_not_found_asset(
        self,
        identifier: AssetIdentifier,
        resume: bool = False
    ):
        tracking_status = "<b>[[[TRACKING RESUME]]]</b>" if resume else "<b>[[[TRACKING STARTED]]]</b>"
        caption = f"""
<b>[NOT FOUND]</b>
{self.chat.group_username or ""}
The asset HAS NOT BEEN FOUND in OpenSea.
- Contract address: {identifier.contract_address}
- Token: {identifier.token_id}

{tracking_status}"""

        self.bot.send_message(
            chat_id=self.chat.id,
            text=caption,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )

    def notify_not_created_asset(self, asset: Asset, resume: bool = False):
        tracking_status = "<b>[[[TRACKING RESUME]]]</b>" if resume else "<b>[[[TRACKING STARTED]]]</b>"
        caption = f"""
<b>[NOT LISTED]</b>
{self.chat.group_username or ""}
The asset HAS BEEN FOUND but NOT LISTED in OpenSea.
{asset.info}

{tracking_status}"""
        self.__send_photo_or_message(asset.image_url, caption=caption)

    def notify_created_asset(self, asset: Asset):
        caption = fr"""
<b>[LISTED]</b>
{self.chat.group_username or ""}
The asset HAS BEEN LISTED in OpenSea.
{asset.info}"""
        self.__send_photo_or_message(asset.image_url, caption=caption)

    def debug(self, asset_identifier: AssetIdentifier):
        if config.DEBUG:
            try:
                self.bot.send_message(
                    chat_id=self.chat.id,
                    text=asset_identifier.to_str()
                )
            except telegram.error.RetryAfter:
                print('Flood control exceeded')
            except telegram.error.TimedOut:
                print('Timed out')

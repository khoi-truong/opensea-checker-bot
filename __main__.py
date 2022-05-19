import argparse
import logging

from telegram.ext import CommandHandler, Updater

import config
from poller import AssetPoller, ResumePollingAssetThread
from tracker import AssetTracker
from users import Users

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def __main() -> None:
    parser = argparse.ArgumentParser(description='ArgumentParser')
    parser.add_argument(
        '-d', '--debug', action='store_true', help='Debug mode')
    parser.add_argument('-i', '--interval', action='store',
                        dest='interval', type=int, default=config.INTERVAL)
    args = parser.parse_args()
    config.DEBUG = args.debug
    config.INTERVAL = args.interval
    updater = Updater(token=config.TOKEN)
    poller = AssetPoller()
    poller.set_bot(updater.bot)
    ResumePollingAssetThread(bot=updater.bot).start()
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler(
        'track', AssetTracker.track, run_async=True))
    dispatcher.add_handler(CommandHandler(
        'untrack', AssetTracker.untrack, run_async=True))
    dispatcher.add_handler(CommandHandler(
        'list', AssetTracker.list, run_async=True))
    dispatcher.add_handler(CommandHandler(
        'add_user', Users.add, run_async=True))
    dispatcher.add_handler(CommandHandler(
        'remove_user', Users.remove, run_async=True))
    dispatcher.add_handler(CommandHandler(
        'list_user', Users.list, run_async=True))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    __main()

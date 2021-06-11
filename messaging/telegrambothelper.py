from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from api.coinmarketcap import CoinMarketCap


class TelegramBotHelper:
    @staticmethod
    def _button(update: Update, context: CallbackContext):
        '''Parses the CallbackQuery and updates the message text.'''
        query = update.callback_query
        query.answer()

        if query.data == 'status':
            response_msg = 'Shows the current status of the bot.\n\n' \
                           '<i>Usage:</i>\n' \
                           '<pre language="python">/status</pre>'
        else:
            response_msg = 'TODO LATER'

        query.edit_message_text(text=response_msg)

    def _set_logger(self, logger):
        self.logger = logger

    def _set_config(self, config):
        self.config = config

    def _status(self, update, context):
        self.logger.info('_status is called')

        response_msg = '<b><i>@{bot_name}</i></b> is up and running...\n\n' \
                       'Enter /help for help'.format(bot_name=self.config.get_telegram_bot_name())

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)

    def _help(self, update, context):
        self.logger.info('_help is called')

        response_msg = '<b>List of available commands:</b>\n\n' \
                       '<b>/status</b>: Shows status\n' \
                       '<b>/setccy</b>: Sets the base currency\n' \
                       '<b>/getccy</b>: Shows the base currency\n' \
                       '<b>/getprice</b>: Shows the current price\n' \
                       '<b>/getdetail</b>: Shows the detailed pricedata\n' \
                       '<b>/setalert</b>: Sets an alert\n' \
                       '<b>/getalerts</b>: Lists all the active alerts\n' \
                       '<b>/deletealert</b>: Deletes an alert'

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)

        keyboard = [
            [InlineKeyboardButton('/status', callback_data='status')],
            [
                InlineKeyboardButton('/setccy', callback_data='setccy'),
                InlineKeyboardButton('/getccy', callback_data='getccy'),
            ],
            [
                InlineKeyboardButton('/getprice', callback_data='getprice'),
                InlineKeyboardButton('/getdetail', callback_data='getdetail'),
            ],
            [
                InlineKeyboardButton('/setalert', callback_data='setalert'),
                InlineKeyboardButton('/getalerts', callback_data='getalerts'),
                InlineKeyboardButton('/deletealert', callback_data='deletealert'),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        response_msg = 'Select a command for detailed help:'

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg, reply_markup=reply_markup)

    def _get_price(self, update, context):
        if len(context.args) < 1:
            response_msg = f'❌ No Cryptocurrency provided.\n\nEnter /help for help.'
        else:
            crypto = context.args[0].upper()
            base_ccy = 'SGD'  # TODO

            self.logger.info(f'_get_price is called for {crypto}')

            cmc = CoinMarketCap(self.config, self.logger)
            status, data, error = cmc.get_quotes_latest(crypto, base_ccy)

            if status:
                if data.percent_change_1h >= 0:
                    emoji = '🙂'
                else:
                    emoji = '😟'

                response_msg = f'{emoji} The current price of <i>{data.name} ({crypto})</i>: ' \
                               f'<b>{data.price:,.4f} {data.convert_ccy}</b>'
            else:
                response_msg = f'❌ Price could not be fetched.\n\nError: <i>{error.error_message}</i>'

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)

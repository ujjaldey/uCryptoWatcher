from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from telegram.ext import CallbackContext

from api.coinmarketcap import CoinMarketCap
from database.alerthelper import AlertHelper
from model.database.alert import AlertDao
from model.entity.alert import Alert


class TelegramBotHelper:
    def __init__(self):
        self.cmc = CoinMarketCap(self.config, self.logger)
        # self.alert_dao = AlertDao()

    @staticmethod
    def _button(update: Update, context: CallbackContext):
        '''Parses the CallbackQuery and updates the message text.'''
        query = update.callback_query
        query.answer()

        if query.data == 'status':
            response_msg = 'Shows the current status of the bot.\n\n' \
                           '<i>Usage:</i>\n' \
                           '<pre>/status</pre>'
        else:
            response_msg = 'TODO LATER'

        query.edit_message_text(text=response_msg)

    @staticmethod
    def _validate_set_alert_input(args):
        if len(args) < 3 or len(args) > 4:
            response_msg = f'⚠ Invalid arguments.\n\nEnter /help for help.'
            return False, response_msg, -1

        if args[1] not in ('>', '<', '>=', '<=', '='):
            condition_output = args[1].replace('<', '&lt;')
            response_msg = f'⚠ Invalid condition <i>{condition_output}</i>.\n\nEnter /help for help.'
            return False, response_msg, -1

        try:
            if float(args[2]) < 0:
                response_msg = f'⚠ Alert price <i>{args[2]}</i> cannot be negative.' \
                               '\n\nEnter /help for help.'
                return False, response_msg, -1
        except ValueError as e:
            response_msg = f'⚠ Alert price <i>{args[2]}</i> should be a number.' \
                           '\n\nEnter /help for help.'
            return False, response_msg, -1

        # get the optiona 4th arg. should be number and end with x
        if len(args) == 4:
            alert_counter_str = args[3]

            if not alert_counter_str.upper().endswith('X'):
                response_msg = f'⚠ Alert counter <i>{alert_counter_str}</i> should end with \'x\'.' \
                               '\n\nEnter /help for help.'
                return False, response_msg, 0

            try:
                if int(alert_counter_str[:-1]) <= 0:
                    response_msg = f'⚠ Alert counter <i>{alert_counter_str[:-1]}</i> should be ' \
                                   'greater than zero.\n\nEnter /help for help.'
                    return False, response_msg, 0
            except ValueError as e:
                response_msg = f'⚠ Alert counter <i>{alert_counter_str[:-1]}</i> should be an integer.' \
                               '\n\nEnter /help for help.'
                return False, response_msg, 0

            return True, None, int(alert_counter_str[:-1])
        else:
            return True, None, 0

        return True, None, 0

    def _set_logger(self, logger):
        self.logger = logger

    def _set_config(self, config):
        self.config = config

    def _set_db(self, db):
        self.db = db
        self.conn = db.connect()

    def _set_coinmarketcap(self, cmc):
        self.cmd = cmc

    def _status(self, update: Update, context: CallbackContext):
        self.logger.info('_status is called')

        response_msg = '<b><i>@{bot_name}</i></b> is up and running...\n\n' \
                       'Enter /help for help'.format(bot_name=self.config.get_telegram_bot_name())

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)

    def _help(self, update: Update, context: CallbackContext):
        self.logger.info('_help is called')

        print(update.effective_chat.id)
        response_msg = '<b>List of available commands:</b>\n\n' \
                       '<b>/status</b>: Shows status\n' \
                       '<b>/getprice</b>: Shows the current price\n' \
                       '<b>/getdetail</b>: Shows the detailed pricedata\n' \
                       '<b>/setalert</b>: Sets an alert\n' \
                       '<b>/getalerts</b>: Lists all the active alerts\n' \
                       '<b>/deletealert</b>: Deletes an alert'

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)

        keyboard = [
            [InlineKeyboardButton('/status', callback_data='status')],
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

    def _get_price(self, update: Update, context: CallbackContext):
        if len(context.args) < 1:
            response_msg = f'❌ No Cryptocurrency provided.\n\nEnter /help for help.'
        else:
            crypto = context.args[0].upper()
            base_ccy = self.config.get_base_ccy()

            self.logger.info(f'_get_price is called for {crypto}')

            status, data, error = self.cmc.get_quotes_latest(crypto, base_ccy)

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

    def _get_detail(self, update: Update, context: CallbackContext):
        if len(context.args) < 1:
            response_msg = f'❌ No Cryptocurrency provided.\n\nEnter /help for help.'
        else:
            crypto = context.args[0].upper()
            base_ccy = self.config.get_base_ccy()

            self.logger.info(f'_get_detail is called for {crypto}')

            status, data, error = self.cmc.get_quotes_latest(crypto, base_ccy)

            if status:
                if data.percent_change_1h >= 0:
                    emoji = '🙂'
                else:
                    emoji = '😟'

                price = data.price
                percent_change_1h = data.percent_change_1h
                price_change_1h = price * percent_change_1h / 100
                percent_change_24h = data.percent_change_24h
                price_change_24h = price * percent_change_24h / 100
                percent_change_7d = data.percent_change_7d
                price_change_7d = price * percent_change_7d / 100
                percent_change_30d = data.percent_change_30d
                price_change_30d = price * percent_change_30d / 100
                percent_change_60d = data.percent_change_60d
                price_change_60d = price * percent_change_60d / 100
                percent_change_90d = data.percent_change_90d
                price_change_90d = price * percent_change_90d / 100

                response_msg = f'{emoji} The detailed price data for <i>{data.name} ({crypto})</i>:\n' \
                               f'Current Price: <b>{price:,.4f} {data.convert_ccy}</b>\n' \
                               f'Price Change in 1 hr: <b>{price_change_1h:,.2f} {data.convert_ccy}</b> ' \
                               f'({percent_change_1h:.2f}%)\n' \
                               f'Price Change in 24 hr: <b>{price_change_24h:,.2f} {data.convert_ccy}</b> ' \
                               f'({percent_change_24h:.2f}%)\n' \
                               f'Price Change in 7 days: <b>{price_change_7d:,.2f} {data.convert_ccy}</b> ' \
                               f'({percent_change_7d:.2f}%)\n' \
                               f'Price Change in 30 days: <b>{price_change_30d:,.2f} {data.convert_ccy}</b> ' \
                               f'({percent_change_30d:.2f}%)\n' \
                               f'Price Change in 60 days: <b>{price_change_60d:,.2f} {data.convert_ccy}</b> ' \
                               f'({percent_change_60d:.2f}%)\n' \
                               f'Price Change in 90 days: <b>{price_change_90d:,.2f} {data.convert_ccy}</b> ' \
                               f'({percent_change_90d:.2f}%)\n'
            else:
                response_msg = f'❌ Price could not be fetched.\n\nError: <i>{error.error_message}</i>'

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)

    def _set_alert(self, update: Update, context: CallbackContext):
        success, response_msg, max_alert_counter = self._validate_set_alert_input(context.args)

        if not success:
            context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)
            return

        crypto = context.args[0].upper()
        condition = context.args[1]
        alert_price = float(context.args[2])
        base_ccy = self.config.get_base_ccy()

        max_alert_counter = int(self.config.get_max_alert_counter()) if max_alert_counter == 0 else max_alert_counter

        print(update)
        print(context)
        print(max_alert_counter)

        self.logger.info(f'_get_detail is called for {crypto}')

        status, data, error = self.cmc.get_quotes_latest(crypto, base_ccy)

        if status:
            if data.percent_change_1h >= 0:
                emoji = '🙂'
            else:
                emoji = '😟'

            if condition == '>':
                condition_desc = 'greater than'
            elif condition == '<':
                condition_desc = 'less than'
            elif condition == '>=':
                condition_desc = 'greater than or equals to'
            elif condition == '<=':
                condition_desc = 'less than or equals to'
            elif condition == '=':
                condition_desc = 'equals to'
            else:
                condition_desc = ''

            response_msg = f'⏳ Alert set for <i>{data.name} ({crypto})</i> ' \
                           f'price is <i>{condition_desc}</i> <b>{alert_price:,.4f} {base_ccy}</b>.\n\n' \
                           f'{emoji} The current price of <i>{data.name} ({crypto})</i>: ' \
                           f'<b>{data.price:,.4f} {data.convert_ccy}</b>'
        else:
            response_msg = f'❌ Price could not be fetched.\n\nError: <i>{error.error_message}</i>'

        context.job_queue.run_repeating(self._set_alert_callback,
                                        interval=int(self.config.get_alert_frequency_sec()),
                                        context=['hiii', update.message.chat_id])

        alert_data = Alert(chat_id=update.message.chat_id, crypto=crypto, condition=condition, alert_price=alert_price,
                           base_ccy=base_ccy, max_alert_count=5, active='Y', last_alert_at='')

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)

        alert_helper = AlertHelper(self.logger)
        result, error = alert_helper.insert(self.db.connect(), alert_data)

        if not result:
            response_msg = f'❌ Alert could not be saved.\n\nError: <i>{error}</i>'
            context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)

    def _set_alert_callback(self, context):
        print('context')
        print(context)
        print(context.job.context[0])
        context.bot.send_message(chat_id=context.job.context[1], text='hiiii')

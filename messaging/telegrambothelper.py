from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext

from api.coinmarketcap import CoinMarketCap
from database.alerthelper import AlertHelper
from model.entity.alert import Alert


class TelegramBotHelper:
    ALERT = 'alert'
    ALERT_CALLBACK = 'alert_callback'

    def __init__(self):
        self.cmc = CoinMarketCap(self.config, self.logger)

    def _delete_alert_callback(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        alert_id = int(query.data.split('_')[1])

        if alert_id <= 0:
            response_msg = '⚠ No alert selected for delete\n\n'
        else:
            alert_helper = AlertHelper(self.logger)
            result, error = alert_helper.update_active_flg(self.db.connect(), alert_id, 'N')

            if not result:
                response_msg = f'❌ Alert could not be updated.\n\nError: <i>{error}</i>'
            else:
                response_msg = f'🟢 Alert successfully deleted.'

        query.edit_message_text(text=response_msg)

    def _detailed_help(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        help_topic = query.data.split('_')[1]

        if help_topic == 'status':
            response_msg = 'ℹ Shows the current status of the bot.\n\n' \
                           '<i>Usage:</i>\n' \
                           '<pre>/status</pre>'
        elif help_topic == 'getprice':
            response_msg = 'ℹ Gets the current price of a cryptocurrency.\n\n' \
                           '<i>Usage:</i>\n' \
                           '<pre>/getprice CCY\nCCY: Cryptocurrency code</pre>\n\n' \
                           '<i>Example:</i>\n' \
                           '<pre>/getprice BTC</pre>'
        elif help_topic == 'getdetail':
            response_msg = 'ℹ Gets the detailed price of a cryptocurrency.\n\n' \
                           '<i>Usage:</i>\n' \
                           '<pre>/getdetail CCY\nCCY: Cryptocurrency code</pre>\n\n' \
                           '<i>Example:</i>\n' \
                           '<pre>/getdetail BTC</pre>'
        elif help_topic == 'setalert':
            response_msg = 'ℹ Sets an alert for the Cryptocurrency price matching the given criteria.\n\n' \
                           '<i>Usage:</i>\n' \
                           '<pre>/setalert CCY CONDITION PRICE Nx\n' \
                           'CCY: Cryptocurrency code\n' \
                           'CONDITION: >, &lt;, >=, &lt;=, =\nPRICE: Alert rice in Base currency\n' \
                           f'N: Repeat times (default {self.config.get_max_alert_count()})</pre>\n\n' \
                           '<i>Example:</i>\n' \
                           '<pre>/setalert BTC > 40000</pre>\n' \
                           '<pre>/setalert BTC &lt; 35000 3x</pre>\n'
        elif help_topic == 'getalerts':
            response_msg = 'ℹ Gets the list of active alerts.\n\n' \
                           '<i>Usage:</i>\n' \
                           '<pre>/getalerts</pre>'
        elif help_topic == 'deletealert':
            response_msg = 'ℹ Deletes an actie alert.\n\n' \
                           '<i>Usage:</i>\n' \
                           '<pre>/deletealert</pre>'
        else:
            response_msg = '❌ Invalid command for help'

        query.edit_message_text(text=response_msg)

    @staticmethod
    def _validate_set_alert_input(args):
        if len(args) < 3 or len(args) > 4:
            response_msg = f'⚠ Invalid arguments.\n\nTry /help for help.'
            return False, response_msg, -1

        if args[1] not in ('>', '<', '>=', '<=', '='):
            condition_output = args[1].replace('<', '&lt;')
            response_msg = f'⚠ Invalid condition <i>{condition_output}</i>.\n\nTry /help for help.'
            return False, response_msg, -1

        try:
            if float(args[2]) < 0:
                response_msg = f'⚠ Alert price <i>{args[2]}</i> cannot be negative.' \
                               '\n\nTry /help for help.'
                return False, response_msg, -1
        except ValueError as e:
            response_msg = f'⚠ Alert price <i>{args[2]}</i> should be a number.' \
                           '\n\nTry /help for help.'
            return False, response_msg, -1

        if len(args) == 4:
            alert_count_str = args[3]

            if not alert_count_str.upper().endswith('X'):
                response_msg = f'⚠ Alert count <i>{alert_count_str}</i> should end with \'x\'.' \
                               '\n\nTry /help for help.'
                return False, response_msg, 0

            try:
                if int(alert_count_str[:-1]) <= 0:
                    response_msg = f'⚠ Alert count <i>{alert_count_str[:-1]}</i> should be ' \
                                   'greater than zero.\n\nTry /help for help.'
                    return False, response_msg, 0
            except ValueError as e:
                response_msg = f'⚠ Alert count <i>{alert_count_str[:-1]}</i> should be an integer.' \
                               '\n\nTry /help for help.'
                return False, response_msg, 0

            return True, None, int(alert_count_str[:-1])
        else:
            return True, None, 0

        return True, None, 0

    def _get_response_msg(self, status, data, error, alert_price, condition, base_ccy, alert_count, response_type):
        if status:
            if data.percent_change_1h >= 0:
                emoji_up_down = '👍'
            else:
                emoji_up_down = '👎'

            if condition == '>':
                condition_desc = 'greater than'
            elif condition == '<':
                condition_desc = 'lesser than'
            elif condition == '>=':
                condition_desc = 'greater than or equal to'
            elif condition == '<=':
                condition_desc = 'lesser than or equal to'
            elif condition == '=':
                condition_desc = 'equal to'
            else:
                condition_desc = ''

            if response_type == self.ALERT_CALLBACK:
                tmp_str = str(alert_count)
                emoji = '⏳'
            else:
                tmp_str = 'set'
                emoji = '🔔'

            response_msg = f'{emoji} Alert <i>{tmp_str}</i> for <i>{data.name} ({data.symbol})</i> ' \
                           f'price is <i>{condition_desc}</i> <b>{alert_price:,.4f} {base_ccy}</b>.\n\n' \
                           f'{emoji_up_down} The current price of <i>{data.name} ({data.symbol})</i>: ' \
                           f'<b>{data.price:,.4f} {data.convert_ccy}</b>'
        else:
            response_msg = f'❌ Price could not be fetched.\n\nError: <i>{error.error_message}</i>'

        return response_msg

    def _set_logger(self, logger):
        self.logger = logger

    def _set_config(self, config):
        self.config = config

    def _set_db(self, db):
        self.db = db
        self.conn = db.connect()

    def _set_coinmarketcap(self, cmc):
        self.cmd = cmc

    def _invalid_command(self, update: Update, context: CallbackContext):
        self.logger.info('_invalid_command is called')

        response_msg = f'⚠ Invalid Command {update.message.text}\n\nTry /help for help' \
            .format(bot_name=self.config.get_telegram_bot_name())

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)

    def _status(self, update: Update, context: CallbackContext):
        self.logger.info('_status is called')

        response_msg = 'ℹ <b><i>@{bot_name}</i></b> is up and running\n\n' \
                       'Try /help for help'.format(bot_name=self.config.get_telegram_bot_name())

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)

    def _help(self, update: Update, context: CallbackContext):
        self.logger.info('_help is called')

        response_msg = '<b>List of available commands:</b>\n\n' \
                       '<b>/status</b>: Shows status\n' \
                       '<b>/getprice</b>: Shows the current price\n' \
                       '<b>/getdetail</b>: Shows the detailed pricedata\n' \
                       '<b>/setalert</b>: Sets an alert\n' \
                       '<b>/getalerts</b>: Lists all the active alerts\n' \
                       '<b>/deletealert</b>: Deletes an alert'

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)

        keyboard = [
            [InlineKeyboardButton('/status', callback_data='help_status')],
            [
                InlineKeyboardButton('/getprice', callback_data='help_getprice'),
                InlineKeyboardButton('/getdetail', callback_data='help_getdetail'),
            ],
            [
                InlineKeyboardButton('/setalert', callback_data='help_setalert'),
                InlineKeyboardButton('/getalerts', callback_data='help_getalerts'),
                InlineKeyboardButton('/deletealert', callback_data='help_deletealert'),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        response_msg = 'Select a command for detailed help:'

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg, reply_markup=reply_markup)

    def _get_price(self, update: Update, context: CallbackContext):
        if len(context.args) < 1:
            response_msg = f'❌ No Cryptocurrency provided.\n\nTry /help for help.'
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
            response_msg = f'❌ No Cryptocurrency provided.\n\nTry /help for help.'
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
        success, response_msg, max_alert_count = self._validate_set_alert_input(context.args)

        if not success:
            context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)
            return

        crypto = context.args[0].upper()
        condition = context.args[1]
        alert_price = float(context.args[2])
        base_ccy = self.config.get_base_ccy()
        alert_count = 0

        max_alert_count = int(self.config.get_max_alert_count()) if max_alert_count == 0 else max_alert_count

        self.logger.info(f'_set_alert is called for {crypto}')

        status, data, error = self.cmc.get_quotes_latest(crypto, base_ccy)

        response_msg = self._get_response_msg(status, data, error, alert_price, condition, base_ccy, 0, self.ALERT)

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)

        if status:
            alert_data = Alert(chat_id=update.message.chat_id, crypto=crypto, condition=condition,
                               alert_price=alert_price,
                               base_ccy=base_ccy, max_alert_count=max_alert_count, active='Y', last_alert_at='')

            alert_helper = AlertHelper(self.logger)
            result, output = alert_helper.insert(self.db.connect(), alert_data)

            context.job_queue.run_repeating(self._set_alert_callback,
                                            interval=int(self.config.get_alert_frequency_sec()),
                                            context=[crypto, condition, alert_price, base_ccy,
                                                     update.message.chat_id, max_alert_count, alert_count, output])

            if not result:
                response_msg = f'❌ Alert could not be saved.\n\nError: <i>{output}</i>'
                context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)

    def _set_alert_callback(self, context):
        crypto = context.job.context[0]
        condition = context.job.context[1]
        alert_price = context.job.context[2]
        base_ccy = context.job.context[3]
        chat_id = context.job.context[4]
        max_alert_count = context.job.context[5]
        alert_count = context.job.context[6]
        alert_id = context.job.context[7]

        self.logger.info(f'_set_alert_callback is called for {crypto}')

        status, data, error = self.cmc.get_quotes_latest(crypto, base_ccy)

        if condition == '>' and float(data.price) > float(alert_price):
            show_alert = True
        elif condition == '<' and float(data.price) < float(alert_price):
            show_alert = True
        elif condition == '>=' and float(data.price) >= float(alert_price):
            show_alert = True
        elif condition == '<=' and float(data.price) <= float(alert_price):
            show_alert = True
        elif condition == '=' and float(data.price) == float(alert_price):
            show_alert = True
        else:
            show_alert = False

        if show_alert:
            alert_count += 1
            response_msg = self._get_response_msg(status, data, error, alert_price, condition, base_ccy, alert_count,
                                                  self.ALERT_CALLBACK)

            context.job.context[6] = alert_count

            context.bot.send_message(chat_id=chat_id, text=response_msg)

            alert_data = Alert(id=alert_id, chat_id=chat_id, crypto=crypto, condition=condition,
                               alert_price=alert_price, base_ccy=base_ccy, max_alert_count=max_alert_count,
                               alert_count=alert_count, active='Y', last_alert_at=datetime.now().replace(microsecond=0),
                               updated_at=datetime.now().replace(microsecond=0))

            alert_helper = AlertHelper(self.logger)
            result1, error1 = alert_helper.update_alert_count(self.db.connect(), alert_data, alert_count)

            if alert_count >= max_alert_count:
                context.job.schedule_removal()
                result2, error2 = alert_helper.update_active_flg(self.db.connect(), alert_id, 'N')
            else:
                result2, error2 = True, None

            if not (result1 and result2):
                error = error1 if error1 else ''
                error = error + '\n' + (error2 if error2 else '')
                response_msg = f'❌ Alert could not be updated.\n\nError: <i>{error}</i>'
                context.bot.send_message(chat_id=chat_id, text=response_msg)

    def _get_alerts(self, update: Update, context: CallbackContext):
        self.logger.info(f'_get_alerts is called')

        alert_helper = AlertHelper(self.logger)
        result, output = alert_helper.select(self.db.connect())

        if len(output) == 0:
            response_msg = '🚫 No active alerts'
        else:
            response_msg = '📃 List of active alerts:\n\n'

            for rec in output:
                condition_str = rec.condition.replace('<', '&lt;')
                response_msg += f'{rec.crypto} {condition_str} {rec.alert_price:,.4f} {rec.base_ccy}' \
                                f'{rec.max_alert_count}x (pending {rec.max_alert_count - rec.alert_count})\n'

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)

    def _delete_alert(self, update: Update, context: CallbackContext):
        self.logger.info('_delete_alert is called')

        alert_list_buttons = []

        alert_helper = AlertHelper(self.logger)
        result, output = alert_helper.select(self.db.connect())

        if len(output) == 0:
            response_msg = '🚫 No active alerts'
        else:
            response_msg = 'Select an alert to delete:'

            for rec in output:
                alert_str = f'{rec.crypto} {rec.condition} {rec.alert_price:,.4f} {rec.base_ccy}' \
                            f'{rec.max_alert_count}x (pending {rec.max_alert_count - rec.alert_count})\n'

                alert_list_buttons.append([InlineKeyboardButton(alert_str, callback_data=f'delete_{rec.id}')])

        reply_markup = InlineKeyboardMarkup(alert_list_buttons)

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg, reply_markup=reply_markup)

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class TelegramBotHelper:
    def _set_logger(self, logger):
        self.logger = logger

    def _status(self, update, context):
        self.logger.info("_status is called")

        response_msg = '<b><i>@uCryptoWatcherBot</i></b> is up and running...\n\n' \
                       'Enter /help for help'

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)

    def _help(self, update, context):
        self.logger.info("_help is called")

        keyboard = [
            [
                InlineKeyboardButton("/setccy", callback_data='1'),
                InlineKeyboardButton("/getccy", callback_data='2'),
            ],
            [InlineKeyboardButton("Option 3", callback_data='3')],
            [InlineKeyboardButton("Option 4", callback_data='4')],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        response_msg = 'Select a command for help:'

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg, reply_markup=reply_markup)

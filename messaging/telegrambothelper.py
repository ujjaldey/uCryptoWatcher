class TelegramBotHelper:
    def _set_logger(self, logger):
        self.logger = logger

    def _status(self, update, context):
        self.logger.info("_status is called")

        response_msg = '<b><i>@uCryptoWatcherBot</i></b> is up and running...\n\n' \
                       'Enter /help for help'

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)

class Update:
    def __init__(self, update):
        self.id = update['update_id']
        if 'message' in update:
            self.type = 'message'
            self.from_id = update['message']['from']['id']
            self.msg_text = update['message']['text']
        elif 'edited_message' in update:
            self.type = 'message'
            self.from_id = update['message']['from']['id']
        elif 'callback_query' in update:
            self.type = 'callback_query'
            self.cbq_id = update['callback_query']['id']
            self.msg_id = update['callback_query']['message']['message_id']
            self.from_id = update['callback_query']['from']['id']
            self.cbq_data = update['callback_query']['data']
            self.msg_text = update['callback_query']['message']['text']
            self.reply_mu = update['callback_query']['message']['reply_markup']

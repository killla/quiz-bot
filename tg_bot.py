from functools import partial
import logging.config
import random

from environs import Env
import redis
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler

from text_tools import get_questions, check_answer

PLAYING, WIN = range(2)
logger = logging.getLogger('telegramLogger')


def start(bot, update):
    custom_keyboard = [['Новый вопрос', 'Сдаться'],
                       ['Мой счет']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.effective_chat.id,
                    text = "Привет. Это викторина",
                    reply_markup=reply_markup)
    return WIN


def handle_new_question_request(bot, update, questions, db):
    chat_id = update.effective_chat.id
    question = random.choice(list(questions))
    db.set(f'tg-{chat_id}', question)
    update.message.reply_text(question)
    return PLAYING


def handle_solution_attempt(bot, update, questions, db):
    chat_id = update.effective_chat.id
    right_answer = questions[db.get(f'tg-{chat_id}')]

    if check_answer(right_answer, update.message.text):
        update.message.reply_text('Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»')
        return WIN

    update.message.reply_text('Неправильно… Попробуешь ещё раз?')
    return PLAYING


def handle_give_up(bot, update, questions, db):
    chat_id = update.effective_chat.id
    right_answer = questions[db.get(f'tg-{chat_id}')]
    update.message.reply_text(f'Правильный ответ:\n{right_answer}')

    handle_new_question_request(bot, update, questions, db)


def error(bot, update):
    logger.warning('Update "%s" caused error "%s"', update, error)


def done(bot, update, user_data):
    update.message.reply_text("До встречи")
    user_data.clear()
    return ConversationHandler.END


def process_quiz(token, questions, db):
    updater = Updater(token)
    dp = updater.dispatcher

    p_handle_new_question_request = partial(handle_new_question_request, questions, db)
    p_handle_give_up = partial(handle_give_up, questions, db)
    p_handle_solution_attempt = partial(handle_solution_attempt, questions, db)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            PLAYING: [RegexHandler('^Новый вопрос$',
                                    p_handle_new_question_request),
                      RegexHandler('^Сдаться$',
                                   p_handle_give_up),
                      MessageHandler(Filters.text,
                                     p_handle_solution_attempt)],

            WIN: [RegexHandler('^Новый вопрос$',
                                    handle_new_question_request)],
        },

        fallbacks=[RegexHandler('^Done$', done)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    env = Env()
    env.read_env()
    log_bot_token = env.str('TG_LOG_BOT_TOKEN')
    tg_chat_id = env.str("TG_LOG_CHAT_ID")
    logging.config.fileConfig('logging.conf', defaults={
                    'token': env.str('TG_LOG_BOT_TOKEN'),
                    'chat_id': env.str("TG_LOG_CHAT_ID")})

    logger.info('Телеграм бот запущен')

    folder = env.str('FOLDER', 'quiz_questions/')

    questions = get_questions(folder)

    redis_host = env.str('REDIS_HOST')
    redis_port = env.str('REDIS_PORT')
    redis_password = env.str('REDIS_PASSWORD')
    db = redis.StrictRedis(host=redis_host,
                           port=redis_port,
                           db=0,
                           password=redis_password,
                           decode_responses=True)

    tg_bot_token = env.str('TG_BOT_TOKEN')
    process_quiz(tg_bot_token, questions, db)

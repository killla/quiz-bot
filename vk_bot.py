from functools import partial
import logging.config
import random

from environs import Env
import redis
import vk_api as vk
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkLongPoll, VkEventType

from text_tools import get_questions, check_answer

PLAYING, WIN = range(2)
logger = logging.getLogger('telegramLogger')


def start(event, vk_api):
    keyboard = VkKeyboard()
    keyboard.add_button('Новый вопрос')
    keyboard.add_button('Сдаться')

    vk_api.messages.send(
        user_id=event.user_id,
        message=event.text,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1, 1000)
    )
    return WIN


def handle_new_question_request(event, vk_api, questions, db):
    question = random.choice(list(questions))
    print(question)
    db.set(f'vk-{event.user_id}', questions[question])
    print(questions[db.get(f'vk-{event.user_id}')])
    vk_api.messages.send(
        user_id=event.user_id,
        message=question,
        random_id=random.randint(1, 1000)
    )
    return PLAYING


def handle_solution_attempt(event, vk_api, questions, db):
    send_message = partial(vk_api.messages.send, user_id=event.user_id, random_id=random.randint(1, 1000))
    right_answer = db.get(f'vk-{event.user_id}')

    if check_answer(right_answer, event.text):
        send_message(message='Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»')
        return WIN
    else:
        send_message(message='Неправильно… Попробуешь ещё раз?')
        return PLAYING


def handle_give_up(event, vk_api, questions, db):
    right_answer = db.get(f'vk-{event.user_id}')

    vk_api.messages.send(
        user_id=event.user_id,
        message=f'Правильный ответ:\n{right_answer}',
        random_id=random.randint(1, 1000)
    )
    handle_new_question_request(event, vk_api, questions, db)


def process_quiz(token, questions, db):
    vk_session = vk.VkApi(token=token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == 'Начать':
                state = start(event, vk_api)
            elif event.text == 'Новый вопрос':
                state = handle_new_question_request(event, vk_api, questions, db)
            elif event.text == 'Сдаться' and state != WIN:
                state = handle_give_up(event, vk_api, questions, db)
            elif event.text and state != WIN:
                state = handle_solution_attempt(event, vk_api, questions, db)


if __name__ == "__main__":
    env = Env()
    env.read_env()
    vk_token = env.str('VK_TOKEN')
    log_bot_token = env.str('TG_LOG_BOT_TOKEN')
    tg_chat_id = env.str("TG_LOG_CHAT_ID")
    logging.config.fileConfig('logging.conf', defaults={
                    'token': env.str('TG_LOG_BOT_TOKEN'),
                    'chat_id': env.str("TG_LOG_CHAT_ID")})

    logger.info('Телеграм бот запущен')

    folder = env.str('FOLDER', 'quiz-questions/')

    questions = get_questions(folder)

    redis_host = env.str('REDIS_HOST')
    redis_port = env.str('REDIS_PORT')
    redis_password = env.str('REDIS_PASSWORD')
    db = redis.StrictRedis(host=redis_host, port=redis_port, db=0, password=redis_password, decode_responses=True)
    process_quiz(vk_token, questions, db)

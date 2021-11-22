from itertools import tee
from pathlib import Path
import re


def get_questions_from_file(file):
    def cut_head(text):
        text = text[text.find(":") + 2:]
        text = text.replace('\n', ' ')
        return text

    with open(file, 'r', encoding='KOI8-R') as file:
        raw_qas = file.read().split('\n\n')
        questions, answers = tee(iter(raw_qas))
        next(answers, None)

        for question, answer in zip(questions, answers):
            if (question.strip()).startswith('Вопрос') and \
                    (answer.strip()).startswith('Ответ'):
                yield cut_head(question), cut_head(answer)


def get_questions(folder):
    questions = {}
    path = Path.cwd() / folder
    files = [file for file in path.glob('*.txt')]

    for file in files:
        for question, answer in get_questions_from_file(file):
            questions[question] = answer
    return questions


def check_answer(right_answer, answer):
    right_answer = right_answer.split('.')[0]
    right_answer = re.sub(r'\[.*\]|\(.*\)', '', right_answer).strip()
    return answer == right_answer


if __name__ == '__main__':
    print(get_questions())

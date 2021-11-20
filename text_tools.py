# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
from pathlib import Path
import random
import re


def get_questions_from_file_old():
    with open('quiz-questions/1vs1200.txt', 'r', encoding='KOI8-R') as file:
        data = file.read()
        for qas in data.split('\n\n\n'):
            question, answer = None, None
            for qa in qas.split('\n\n'):
                if qa.startswith('Вопрос'):
                    question = qa[qa.find(":") + 2:]
                if qa.startswith('Ответ'):
                    answer = qa[qa.find(":") + 2:]
            print(question)
            print(answer)
        if any((q := qa).startswith('Вопрос') for qa in qas.split('\n\n')):
            print(q)


def get_questions_from_file(file):
    def cut_head(text):
        text = text[text.find(":") + 2:]
        text = text.replace('\n', ' ')
        return text

    questions = []

    with open(file, 'r', encoding='KOI8-R') as file:
        #data = file.read()
        i = 0
        qas = file.read().split('\n\n')
        while i < len(qas):
            if (q := qas[i].strip()).startswith('Вопрос') and (a := qas[i+1].strip()).startswith('Ответ'):
                # questions.append((cut_head(q),
                #                cut_head(a)))
                i += 1
                yield cut_head(q), cut_head(a)

                # .jpg

                #print(q)
                #print(a)

            i += 1

    #print(questions)
    #print(len(questions))
    # return questions


def get_questions(folder):
    questions = {}
    path = Path.cwd() / folder
    files = [file for file in path.glob('*.txt')]

    for file in files:
        file = random.choice(files)
        for question, answer in get_questions_from_file(file):
            questions[question] = answer
    return questions
    # while True:
    #     file = random.choice(files)
    #     for question, answer in get_questions_from_file(file):
    #         questions[question] = answer
    #
    #     # questions += get_questions_from_file(file)
    #     #print(len(questions))
    #     if len(questions) > 1000:
    #         return questions

def check_answer(right_answer, answer):
    right_answer = right_answer.split('.')[0]
    right_answer = re.sub(r'\[.*\]|\(.*\)', '', right_answer).strip()
    return answer == right_answer


if __name__ == '__main__':
    #print_hi('PyCharm')
    get_questions()

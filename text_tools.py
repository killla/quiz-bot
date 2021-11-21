from pathlib import Path
import re


def get_questions_from_file(file):
    def cut_head(text):
        text = text[text.find(":") + 2:]
        text = text.replace('\n', ' ')
        return text

    with open(file, 'r', encoding='KOI8-R') as file:
        i = 0
        raw_qas = file.read().split('\n\n')
        while i < len(raw_qas):
            if (question := raw_qas[i].strip()).startswith('Вопрос') and \
                    (answer := raw_qas[i+1].strip()).startswith('Ответ'):
                i += 1
                yield cut_head(question), cut_head(answer)
            i += 1


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

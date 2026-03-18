import re
import random
import json

from pyexpat.errors import messages


def read_txt(file):
    with open(file, 'r', encoding = 'utf-8') as f:
        text=f.read().lower()
        words = re.findall(r'[a-zа-яё]+', text)
        return words

def create_markov_matrix(words, n):
    matrix = {}
    for i in range(len(words) - n):
        key = tuple(words[i : i + n]) # организация цепи и скользящего окна
        new_word = words[i + n]
        if key not in matrix:
            matrix[key] = {}
        matrix[key][new_word]=matrix[key].get(new_word, 0) + 1 # подсчет кол встречаемых слов после состояние (для каждого)
    for key in matrix:
        matrix[key]=dict(sorted(matrix[key].items(), key = lambda item: item[1], reverse= True))
    return matrix

def generate_markov_text (markov_dict, text_len):
    if not markov_dict:
        return "Ошибка: отсутсвует markov_dict"
    current = random.choice(list(markov_dict.keys()))
    text = list(current)
    n = len(current)
    while len(text) < text_len:
        if current in markov_dict:
            arguments = markov_dict[current]
            total_count = sum(arguments.values()) # считаем общее количество возможных переходом из этого состояния
            pilot = random.random()
            accumulation_sums = 0
            for word, count in arguments.items():
                accumulation_sums += count/ total_count
                if pilot <= accumulation_sums:
                    text.append(word)
                    break
            current = tuple(text[-n:])
        else:
            current =random.choice(list(markov_dict.keys()))
    return " ".join(text)

def processing(file, n, text_len):
    try:
        words = read_txt(file)

        if len(words) == 0:
            return {
                "status": "failed",
                "error_message": f"Не смогли найти слова в файле: {file} "
            }
        matrix =create_markov_matrix(words, n)
        result = generate_markov_text(matrix, text_len)
        return  {
            "status": "success",
            "data": result
        }
    except FileNotFoundError:
        return {
            "status": "failed",
            "error_message": f"Файл не найден "
        }
    except Exception as e:
        return{
            "status": "failed",
            "error_message": f"Ошибка: {str(e)}"
        }

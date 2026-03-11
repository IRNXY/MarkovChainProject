import random


def generate_markov_text(markov_dict, text_len):
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
                accumulation_sums += count / total_count
                if pilot <= accumulation_sums:
                    text.append(word)
                    break
            current = tuple(text[-n:])
        else:
            current = random.choice(list(markov_dict.key()))
    return " ".join(text)


def create_markov_matrix(words, n):
    matrix = {}
    for i in range(len(words) - n):
        key = tuple(words[i: i + n]) # организация цепи и скользящего окна
        new_word = words[i + n]
        if key not in matrix:
            matrix[key] = {}
        matrix[key][new_word] = matrix[key].get(new_word, 0) + 1 # подсчет кол встречаемых слов после состояние (для каждого)
    for key in matrix:
        matrix[key] = dict(sorted(matrix[key].items(), key=lambda item: item[1], reverse=True))
    return matrix

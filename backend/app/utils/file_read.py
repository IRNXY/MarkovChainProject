import re


def read_txt(txt):
    # with open(file, 'r', encoding='utf-8') as f:
    #     text = f.read().lower()
    #     words = re.findall(r'[a-zа-яё]+', text)
    #     return words

    text = txt.lower()
    words = re.findall(r'[a-zа-яё]+', text)
    return words

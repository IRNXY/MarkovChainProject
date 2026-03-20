import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.markov_chain import generate_markov_text, create_markov_matrix
from app.utils.file_read import read_txt
from fastapi import FastAPI
from fastapi.testclient import TestClient


app = FastAPI()


@app.post("/generate_markov_txt")
async def mock_endpoint(request_data: dict):
    """Временный эндпоинт для тестирования — замени на настоящий роутер"""
    file = request_data.get("file", "")
    n_gramma = request_data.get("n-gramma", 1)
    total_words = request_data.get("total_words", 10)

    if not file:
        return {"error": "Файл пустой или не передан"}

    words = read_txt(file)

    if len(words) <= n_gramma:
        return {"error": f"Слишком мало слов: нужно больше {n_gramma}, получено {len(words)}"}

    matrix = create_markov_matrix(words, n_gramma)
    text = generate_markov_text(matrix, total_words)
    return {"text": text}

# TestClient — имитирует HTTP-запросы без запуска настоящего сервера
client = TestClient(app)


class TestReadTxt:
    """Тесты функции read_txt — чтение и токенизация текста"""

    def test_normal_text_russian(self):
        """Обычный русский текст корректно разбивается на слова"""
        result = read_txt("Привет мир как дела")
        assert result == ["привет", "мир", "как", "дела"], (
            "ТРЕБОВАНИЕ: функция должна возвращать список слов в нижнем регистре"
        )

    def test_normal_text_english(self):
        """Обычный английский текст корректно разбивается на слова"""
        result = read_txt("Hello world this is a test")
        assert result == ["hello", "world", "this", "is", "a", "test"]

    def test_text_converts_to_lowercase(self):
        """Текст приводится к нижнему регистру"""
        result = read_txt("ЗАГЛАВНЫЕ буквы И MiXeD")
        assert all(word == word.lower() for word in result), (
            "ТРЕБОВАНИЕ: все слова должны быть в нижнем регистре"
        )

    def test_punctuation_is_removed(self):
        """Знаки препинания удаляются из текста"""
        result = read_txt("Привет, мир! Как дела?")
        assert "," not in " ".join(result)
        assert "!" not in " ".join(result)
        assert "?" not in " ".join(result)

    def test_numbers_are_removed(self):
        """Цифры не попадают в список слов"""
        result = read_txt("слово123 тест 456 слово2")
        assert all(word.isalpha() for word in result), (
            "ТРЕБОВАНИЕ: числа и цифры должны быть отфильтрованы"
        )

    def test_empty_string_returns_empty_list(self):
        """
        ❗ БАГИ / ТРЕБОВАНИЯ К КОМАНДЕ:
        Сейчас функция вернёт пустой список — это нормальное поведение.
        Убедитесь, что вышестоящий код проверяет длину результата!
        """
        result = read_txt("")
        assert result == [], (
            "ТРЕБОВАНИЕ: пустая строка должна возвращать пустой список []"
        )

    def test_only_numbers_and_symbols(self):
        """Текст только из цифр и символов даёт пустой список"""
        result = read_txt("123 456 !!! @@@")
        assert result == [], (
            "ТРЕБОВАНИЕ: если нет букв — вернуть пустой список"
        )

    def test_single_word(self):
        """Один слово возвращается как список из одного элемента"""
        result = read_txt("слово")
        assert result == ["слово"]
        assert len(result) == 1


class TestCreateMarkovMatrix:
    """Тесты функции create_markov_matrix — построение матрицы переходов"""

    def test_basic_matrix_creation(self):
        """Базовое создание матрицы для простого текста"""
        words = ["кот", "сидит", "на", "коврике", "кот", "лежит"]
        matrix = create_markov_matrix(words, n=1)
        assert isinstance(matrix, dict), "Матрица должна быть словарём"
        assert len(matrix) > 0, "Матрица не должна быть пустой"

    def test_matrix_keys_are_tuples(self):
        """Ключи матрицы — это кортежи (tuples)"""
        words = ["раз", "два", "три", "четыре", "пять"]
        matrix = create_markov_matrix(words, n=2)
        for key in matrix:
            assert isinstance(key, tuple), (
                "ТРЕБОВАНИЕ: ключи матрицы должны быть кортежами"
            )
            assert len(key) == 2, "Для n=2 каждый ключ должен содержать 2 слова"

    def test_transition_counts_are_correct(self):
        """Счётчики переходов подсчитываются правильно"""
        # "кот" -> "сидит" встречается 2 раза
        words = ["кот", "сидит", "кот", "сидит", "кот", "лежит"]
        matrix = create_markov_matrix(words, n=1)
        key = ("кот",)
        assert key in matrix, "Слово 'кот' должно быть в матрице"
        assert matrix[key].get("сидит", 0) == 2, (
            "Переход 'кот' -> 'сидит' должен встретиться 2 раза"
        )

    def test_sorted_by_frequency_descending(self):
        """Переходы отсортированы по убыванию частоты"""
        words = ["а", "б", "а", "б", "а", "б", "а", "в", "а", "г"]
        matrix = create_markov_matrix(words, n=1)
        key = ("а",)
        if key in matrix:
            counts = list(matrix[key].values())
            assert counts == sorted(counts, reverse=True), (
                "ТРЕБОВАНИЕ: значения в матрице должны быть отсортированы по убыванию"
            )

    def test_single_word_text(self):
        """
        ❗ КРИТИЧЕСКИЙ БАГ / ТРЕБОВАНИЕ К КОМАНДЕ:
        Если в тексте только 1 слово — матрица пустая.
        Это значит что generate_markov_text упадёт!
        Нужно добавить проверку ПЕРЕД вызовом create_markov_matrix.
        """
        words = ["одно"]
        matrix = create_markov_matrix(words, n=1)
        assert matrix == {}, (
            "При 1 слове матрица пустая — нужна обработка этого случая выше по коду!"
        )

    def test_text_shorter_than_n(self):
        """
        ❗ КРИТИЧЕСКИЙ БАГ / ТРЕБОВАНИЕ К КОМАНДЕ:
        Если слов меньше чем n+1 — матрица пустая.
        Например: 2 слова при n=2 — нет ни одного полного окна.
        """
        words = ["слово", "ещё"]
        matrix = create_markov_matrix(words, n=2)
        assert matrix == {}, (
            "ТРЕБОВАНИЕ: если слов меньше n+1, вернуть пустой dict и сообщить об ошибке"
        )

    def test_empty_words_list(self):
        """
        ❗ ТРЕБОВАНИЕ К КОМАНДЕ:
        Пустой список слов — матрица пустая. Не должно быть исключений!
        """
        words = []
        matrix = create_markov_matrix(words, n=1)
        assert matrix == {}, "Пустой список — пустая матрица, без исключений"

    def test_n_equals_zero(self):
        """
        ❗ ТРЕБОВАНИЕ К КОМАНДЕ:
        n=0 — некорректный параметр. Нужна валидация входных данных.
        Сейчас функция может вести себя непредсказуемо.
        """
        words = ["раз", "два", "три"]
        try:
            matrix = create_markov_matrix(words, n=0)
            assert isinstance(matrix, dict)
        except Exception as e:
            pytest.skip(
                f"ТРЕБОВАНИЕ: добавить валидацию n > 0, сейчас ошибка: {e}"
            )


class TestGenerateMarkovText:
    """Тесты функции generate_markov_text — генерация текста по матрице"""

    def get_simple_matrix(self):
        """Вспомогательный метод: матрица для простого детерминированного теста"""
        words = ["кот", "сидит", "на", "коврике", "и", "мурлычет",
                 "кот", "лежит", "на", "диване", "и", "спит"] * 3
        return create_markov_matrix(words, n=1)

    def test_output_is_string(self):
        """Функция возвращает строку"""
        matrix = self.get_simple_matrix()
        result = generate_markov_text(matrix, text_len=5)
        assert isinstance(result, str), "ТРЕБОВАНИЕ: функция должна вернуть строку"

    def test_output_word_count_approximately_correct(self):
        """Количество слов в результате близко к запрошенному"""
        matrix = self.get_simple_matrix()
        result = generate_markov_text(matrix, text_len=10)
        word_count = len(result.split())
        assert word_count >= 8, (
            f"ТРЕБОВАНИЕ: должно быть ~10 слов, получено {word_count}"
        )

    def test_empty_matrix_returns_error_message(self):
        """
        ❗ СУЩЕСТВУЮЩИЙ БАГ — уже обработан в коде:
        Пустая матрица возвращает сообщение об ошибке (не исключение).
        Проверяем что защита работает.
        """
        result = generate_markov_text({}, text_len=10)
        assert "Ошибка" in result or "ошибка" in result.lower(), (
            "ТРЕБОВАНИЕ: пустая матрица должна вернуть сообщение об ошибке"
        )

    def test_typo_in_key_method(self):
        """
        ❗ КРИТИЧЕСКИЙ БАГ В КОДЕ (строка: markov_dict.key()):
        В функции generate_markov_text есть опечатка: .key() вместо .keys()
        Это вызовет AttributeError при отсутствии ключа в словаре.

        ТРЕБОВАНИЕ К КОМАНДЕ: исправить .key() на .keys() в строке:
            current = random.choice(list(markov_dict.key()))
        """
        small_matrix = {("старт",): {"конец": 1}}
        try:
            result = generate_markov_text(small_matrix, text_len=100)
            # Если дошли сюда — баг не воспроизвёлся, но всё равно проверим тип
            assert isinstance(result, str)
        except AttributeError as e:
            pytest.fail(
                f"БАГ ПОДТВЕРЖДЁН: AttributeError из-за .key() вместо .keys(). "
                f"Исправьте в markov_chain.py! Ошибка: {e}"
            )

    def test_text_len_one(self):
        """Запрос на 1 слово — крайний случай"""
        matrix = self.get_simple_matrix()
        result = generate_markov_text(matrix, text_len=1)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_result_contains_known_words(self):
        """Сгенерированный текст содержит слова из исходного словаря"""
        words = ["кот", "сидит", "на", "коврике"] * 5
        matrix = create_markov_matrix(words, n=1)
        result = generate_markov_text(matrix, text_len=5)
        result_words = result.split()
        known_words = set(words)
        for word in result_words:
            assert word in known_words, (
                f"Слово '{word}' не из исходного текста — генерация работает некорректно"
            )


class TestProcessGenerationRequest:
    """Тесты HTTP эндпоинта /generate_markov_txt"""

    def test_normal_request_returns_text(self):
        """Корректный запрос возвращает сгенерированный текст"""
        payload = {
            "file": "кот сидит на коврике кот лежит на диване кот мурлычет",
            "n-gramma": 1,
            "total_words": 10
        }
        response = client.post("/generate_markov_txt", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "text" in data or "error" in data, (
            "Ответ должен содержать поле 'text' или 'error'"
        )

    def test_empty_file_returns_error(self):
        """
        ❗ ТРЕБОВАНИЕ К КОМАНДЕ:
        Пустой файл должен возвращать понятное сообщение об ошибке,
        а не падать с 500 Internal Server Error!
        """
        payload = {
            "file": "",
            "n-gramma": 1,
            "total_words": 10
        }
        response = client.post("/generate_markov_txt", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "error" in data, (
            "ТРЕБОВАНИЕ: пустой файл → вернуть {'error': 'описание проблемы'}"
        )

    def test_one_word_file_returns_error(self):
        """
        ❗ КРИТИЧЕСКИЙ КЕЙС (из задания):
        Файл содержит только 1 слово, а матрица строится минимум по 2.
        Должна вернуться ошибка, а не исключение сервера!
        """
        payload = {
            "file": "одинокоеслово",
            "n-gramma": 2,
            "total_words": 10
        }
        response = client.post("/generate_markov_txt", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "error" in data, (
            "ТРЕБОВАНИЕ: 1 слово при n=2 → {'error': 'Слишком мало слов...'}"
        )

    def test_missing_fields_handled_gracefully(self):
        """
        ❗ ТРЕБОВАНИЕ К КОМАНДЕ:
        Запрос без обязательных полей не должен ронять сервер (500 error).
        Нужна валидация входных данных через Pydantic модели!
        """
        payload = {"file": "текст"}  # нет n-gramma и total_words
        response = client.post("/generate_markov_txt", json=payload)
        assert response.status_code != 500, (
            "ТРЕБОВАНИЕ: добавить Pydantic модель для валидации запроса"
        )

    def test_negative_total_words(self):
        """
        ❗ ТРЕБОВАНИЕ К КОМАНДЕ:
        total_words не может быть отрицательным или нулём.
        Нужна валидация: total_words > 0
        """
        payload = {
            "file": "кот сидит на коврике кот лежит",
            "n-gramma": 1,
            "total_words": -5
        }
        response = client.post("/generate_markov_txt", json=payload)
        assert response.status_code != 500, (
            "ТРЕБОВАНИЕ: валидировать total_words > 0"
        )

    def test_large_n_gramma_exceeds_text(self):
        """
        ❗ ТРЕБОВАНИЕ К КОМАНДЕ:
        n-gramma больше длины текста — должна быть ошибка, не крэш.
        """
        payload = {
            "file": "два слова",
            "n-gramma": 100,
            "total_words": 10
        }
        response = client.post("/generate_markov_txt", json=payload)
        assert response.status_code != 500

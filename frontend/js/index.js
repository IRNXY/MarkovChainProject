const outputDiv = document.getElementById('output');
const ngramSelect = document.getElementById('ngram');
const totalWordsInput = document.getElementById('totalWords');
const fileInput = document.getElementById('fileInput');
const sendBtn = document.getElementById('sendBtn');
const themeBtn = document.getElementById('themeBtn');

let uploadedText = "";

//переключения темы
if (localStorage.getItem('theme') === 'dark') {
    document.body.classList.add('dark-mode');
}

themeBtn.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
});

//работа с файлом
fileInput.addEventListener('change', function() {
    const file = this.files[0];
    if (file) {
        if (!file.name.endsWith('.txt')) {
                outputDiv.innerText = "Ошибка: Допустимы только файлы формата .txt";
                this.value = ""; //сбрасываем выбор
                uploadedText = "";
                return;
            }
        const reader = new FileReader();
        reader.onload = (e) => {
            uploadedText = e.target.result;
            console.log("Файл прочитан");
        };
        reader.readAsText(file);
    }
});

//функция генерации
async function sendData() {
    if (!uploadedText) {
        outputDiv.innerText = "Сначала загрузите текстовый файл!";
        return;
    }
    const wordsArray = uploadedText.trim().split(/\s+/).filter(word => word.length > 0);
    if (wordsArray.length < 5) {
        outputDiv.innerText = "Ошибка: Текст в файле слишком короткий (нужно минимум 5 слов).";
        return;
    }
    if (wordsArray.length > 1000000) {
        outputDiv.innerText = "Ошибка: Текст в файле слишком длинный (можно максимум 1000000 слов).";
        return;
    }
    const totalWords = parseInt(totalWordsInput.value);
    if (isNaN(totalWords) || totalWords <= 0) {
        outputDiv.innerText = "Ошибка: Введите положительное количество слов для генерации.";
        return;
    }
    if (totalWords > 10000) {
        outputDiv.innerText = "Ошибка: Прости, мы пока что не научились генерировать такие большие тексты.";
        return;
    }
    outputDiv.innerText = "Загрузка...";
    const data = {
        "n-gramma": parseInt(ngramSelect.value),
        "file": uploadedText,
        "total_words": parseInt(totalWordsInput.value)
    };

    try {
        const response = await fetch('http://localhost:8080/api/v1/generate_markov_txt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (result.status === "failed") {
            outputDiv.innerText = "Ошибка сервера: " + (result.error_message || "Неизвестная ошибка");
        } else {
            outputDiv.innerText = result.text || "Сервер вернул пустой результат";
        }
    } catch (error) {
        console.error("Ошибка:", error);
        outputDiv.innerText = "Ошибка: Сервер не отвечает. Повторите попытку позже.";
    }
}

sendBtn.addEventListener('click', sendData);

window.addEventListener('keydown', (event) => {
    if (event.code === "Space" && document.activeElement !== totalWordsInput) {
        event.preventDefault();
        sendData();
    }
});

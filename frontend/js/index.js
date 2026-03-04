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
        outputDiv.innerText = result.text || "Сервер вернул пустой результат";
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
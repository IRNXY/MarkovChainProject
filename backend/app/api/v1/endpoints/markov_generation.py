from fastapi import APIRouter, Request
from ....services.markov_chain import generate_markov_text, create_markov_matrix
from ....utils.file_read import read_txt


router = APIRouter(prefix="/generate_markov_txt", tags=["markov_gen"])


@router.post("")
async def process_generation_request(request: Request):
    """
    Генерирует текст с параметрами n-gramma, file, total_words
    """

    try:
        data = await request.json()

        file = data["file"]
        n_gramma = data["n-gramma"]
        total_words = data["total_words"]

        processed_text = read_txt(file)

        if len(processed_text) == 0:
            return {
                "status": "failed",
                "error_message": f"Не смогли найти слова в файле: {data} "
            }
        markov_matrix = create_markov_matrix(processed_text, n_gramma)

        markov_text = generate_markov_text(markov_matrix, total_words)

        return {
            "status": "success",
            "text": markov_text
        }
    except Exception as e:
        return {
            "status": "failed",
            "error_message": f"Ошибка: {str(e)}"
        }


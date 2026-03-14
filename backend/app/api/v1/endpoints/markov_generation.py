from fastapi import APIRouter, Request
from ....services.markov_chain import generate_markov_text, create_markov_matrix
from ....utils.file_read import read_txt


router = APIRouter(prefix="/generate_markov_txt", tags=["markov_gen"])


@router.post("")
async def process_generation_request(request: Request):
    """
    Генерирует текст с параметрами n-gramma, file, total_words
    """

    data = await request.json()

    file = data["file"]
    n_gramma = data["n-gramma"]
    total_words = data["total_words"]

    processed_text = read_txt(file)

    markov_matrix = create_markov_matrix(processed_text, n_gramma)

    markov_text = generate_markov_text(markov_matrix, total_words)

    return {"text": markov_text}

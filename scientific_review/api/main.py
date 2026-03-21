from fastapi import FastAPI

app = FastAPI()

@app.post("/upload_paper")
async def upload_paper(data: dict):
    file_url = data["file_url"]

    # TODO: скачать PDF
    # TODO: multi-agent

    return {
        "scores": {
            "novelty": 8,
            "scientific": 7,
            "complexity": 6,
            "readability": 9
        },
        "review": "Хорошая статья..."
    }


from fastapi import FastAPI, UploadFile, File
from dotenv import load_dotenv
import fitz  # PyMuPDF
import openai
import os
from openai import OpenAI

# uvicorn main:app --reload
app = FastAPI()
load_dotenv()

"""
그냥 공식 문서 봐라...
https://platform.openai.com/docs/guides/text?api-mode=responses&lang=python
"""

openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()  # 기본적으로 환경변수에서 API 키를 읽음


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    contents = await file.read()

    # PDF를 저장
    filename = file.filename
    save_path = f"uploads/{filename}"
    os.makedirs("uploads", exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(contents)

    # 텍스트 추출
    text = extract_text_from_pdf(save_path)
    return {"filename": filename, "content": text[:1000]}  # 너무 길면 앞부분만 미리보기


def extract_text_from_pdf(path):
    doc = fitz.open(path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text


@app.post("/upload-pdf-summary/")
async def upload_and_summarize(file: UploadFile = File(...)):
    contents = await file.read()
    save_path = f"uploads/{file.filename}"
    with open(save_path, "wb") as f:
        f.write(contents)

    text = extract_text_from_pdf(save_path)
    summary = ask_gpt(f"다음 내용을 요약해줘:\n\n{text[:3000]}")  # 너무 길면 자름
    return {"summary": summary}


# def ask_gpt(prompt):
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",  # 필요시 gpt-4 사용
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0.5,
#     )
#     return response.choices[0].message.content


def ask_gpt(prompt):
    response = client.responses.create(model="gpt-3.5-turbo", input=prompt)

    return response.output_text

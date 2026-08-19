from fastapi import FastAPI
import uvicorn

app = FastAPI(
    title="Exemplo FastAPI",
    description="Exemplo de aplicação FastAPI",
    version="1.0.0",
    contact={
        "name": "Seu Nome",
        "email": "seu.email@exemplo.com"
    },
)

@app.get("/")
def read_root():
    return {"message":"Hello World"}

@app.get("/hello/{name}")
def read_hello(name: str):
    return {"message": f"Hello, {name}!"}

def main():
    uvicorn.run("exemplo1:app", host="localhost", port=8000, reload=True)

if __name__ == "__main__":
    main()
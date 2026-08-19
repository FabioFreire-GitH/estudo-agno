# ----------------------------------------------------------
# Conta Corrente Bancaria - FastAPI
# Gerenciar saques e depositos de clientes
# ----------------------------------------------------------

# IMPORTS ==================================================
from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel, Field

app = FastAPI(title="Conta Bancaria - Conta Corrente")

# Adicionar clientes (simula banco de dados)
db_clientes = {
    "João":500,
    "Maria":0,
    "Pedro":0,
}

# Criar uma classe para as movimentações (saques e depositos) OBS: usar pydantic (para não acontecer erros)
class Movimentacao(BaseModel):
    cliente:str = Field(...,description="Nome do cliente")
    valor: float = Field(..., gt=0, description="Valor da movimentação")

# Criar um endpoit HOME (raiz0)
@app.get("/")
def read_root():
    return {"message":"Conta Bancária - Conta Corrente"}

# Criar um endpoint para consultar o saldo
@app.post("/saldo")
def saldo(cliente: str):
    return {"message":f"Saldo do cliente {cliente} é {db_clientes[cliente]}"}

# Criar um endpoint para realizar saques
@app.post("/saque")
def saque(movimentacao: Movimentacao):
    db_clientes[movimentacao.cliente] -= movimentacao.valor
    return {"message":f"Saque de {movimentacao.valor} realizado com sucesso para o cliente {movimentacao.cliente}. Saldo atual: {db_clientes[movimentacao.cliente]}"}

# Criar um endpoint para realizar depositos
@app.post("/deposito")
def deposito(movimentacao: Movimentacao):
    db_clientes[movimentacao.cliente] += movimentacao.valor
    return {"message":f"Deposito de {movimentacao.valor} realizado com sucesso para o cliente {movimentacao.cliente}. Saldo atual: {db_clientes[movimentacao.cliente]}"}

# RUN =============================================================
def main():
    uvicorn.run("exemplo2:app", host="localhost", port=8000, reload=True)

if __name__ == "__main__":
    main()
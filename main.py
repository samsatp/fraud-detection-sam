from fastapi import FastAPI
from pydantic import BaseModel
from .config import config

class Transaction(BaseModel):
    time_ind: int # Simulation unit of time (step=1 is 1 hour; total 744 steps = 30 days)
    transac_type: str # Transaction type (CASH-IN, CASH-OUT, DEBIT, PAYMENT, TRANSFER)
    amount: float # Transaction amount (local currency)
    src_acc: str # Customer initiating the transaction
    src_bal: float # Initial balance (sender) before transaction
    src_new_bal: float # New balance (sender) after transaction
    dst_acc: str # Transaction recipient
    dst_bal: float # Initial balance (recipient) before transaction (missing for merchants)
    dst_new_bal: float # New balance (recipient) after transaction (missing for merchants)
    is_fraud: bool # Transactions made by fraudulent agents (target)
    is_flagged_fraud: bool # Transactions flagged for illegal attempts (e.g. transferring more than 200,000 in one transaction)

class Prediction(BaseModel):
    is_fraud: bool # Prediction result (fraudulent or not)

app = FastAPI()


@app.get("/")
def read_root():
    return config.model

@app.post("/predict", response_model=Prediction)
def predict(body: Transaction):
    """
    Predict if a transaction is fraudulent based on the provided instance.
    """
    return Prediction(is_fraud=False)


@app.get("/frauds", response_model=list[Transaction])
def get_frauds():
    """
    Returns all transactions previously predicted as fraudulent (pulled from your own DB).
    """
    return []
    
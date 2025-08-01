from contextlib import asynccontextmanager
from fastapi import FastAPI
from config import config
from typing import Optional
import pickle
from .utils import (
    preprocess_data, 
    Transaction, 
    Prediction, 
    save_result,
    Output, 
    get_all_fraud_transactions
)

# hot load the model and scaler
ml_models = {}
@asynccontextmanager
async def lifespan(app: FastAPI):
    # load the model and scaler
    ml_models["model"] = pickle.load(open(config.model_path, 'rb'))
    ml_models["scaler"] = pickle.load(open(config.scaler_path, 'rb'))
    yield
    # Clean up and release the resources
    ml_models.clear()


app = FastAPI(lifespan=lifespan)


@app.post("/predict", response_model=Prediction)
async def predict(body: Transaction) -> Prediction:
    """
    Predicts whether a given transaction is fraudulent.
    The transaction data is processed as follows:
    - The transaction type is checked; if it is not a 'TRANSFER' or 'CASH_OUT', it is immediately classified as not fraudulent.
    - Feature engineering:
        - only these features are used: `transac_type, amount, src_bal, src_new_bal, dst_bal, dst_new_bal`
        - in addition, `day_of_month` and `hour_of_day` are derived from `time_ind`
    - The input features are scaled using a pre-trained standardization scaler.
    - The pre-trained model predicts if the transaction is fraudulent using the scaled input features.
    
    Args:
        body (Transaction): The transaction data to be evaluated.
    Returns:
        Prediction: An object indicating whether the transaction is predicted to be fraudulent.

    """
    x = preprocess_data(body.model_dump())
    if x['transac_type'] == -1:
        # if the transaction type is not TRANSFER or CASH_OUT, return False
        pred = Prediction(pred=False, pred_proba=None)
    else:
        # Scale the input features
        x_scaled = ml_models["scaler"].transform([x])
        # Predict using the pre-trained model
        pred_result = ml_models["model"].predict(x_scaled)
        pred_proba = ml_models["model"].predict_proba(x_scaled)[0][1] if hasattr(ml_models["model"], "predict_proba") else None
        pred = Prediction(pred=bool(pred_result[0]), pred_proba=pred_proba)
    # Save the result to the database
    save_result(prediction=pred, transaction=body)
    return pred

@app.get("/frauds", response_model=list[Output])
async def get_frauds(proba_threshold: Optional[float] = None) -> list[Output]:
    """
    Returns all transactions previously predicted as fraudulent (pulled from your own DB).
    """
    return get_all_fraud_transactions(proba_threshold=proba_threshold)
    
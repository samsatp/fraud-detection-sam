from pydantic import BaseModel
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from typing import Optional, List
from .config import config

class Transaction(BaseModel):
    """
    This data model represents an input transaction entry.
    """
    time_ind:         int # Simulation unit of time (step=1 is 1 hour; total 744 steps = 30 days)
    transac_type:     str # Transaction type (CASH-IN, CASH-OUT, DEBIT, PAYMENT, TRANSFER)
    amount:           float # Transaction amount (local currency)
    src_acc:          Optional[str] = None # Customer initiating the transaction
    src_bal:          float # Initial balance (sender) before transaction
    src_new_bal:      float # New balance (sender) after transaction
    dst_acc:          Optional[str] = None # Transaction recipient
    dst_bal:          float # Initial balance (recipient) before transaction (missing for merchants)
    dst_new_bal:      float # New balance (recipient) after transaction (missing for merchants)
    is_fraud:         Optional[bool] = None # Transactions made by fraudulent agents (target)
    is_flagged_fraud: Optional[bool] = None # Transactions flagged for illegal attempts (e.g. transferring more than 200,000 in one transaction)

class Features(BaseModel):
    """
    This data model represents the features used for prediction.
    It includes the preprocessed fields from the Transaction model.
    """
    transac_type: int # Encoded transaction type (1 for TRANSFER, 0 for CASH_OUT, or -1 for others)
    amount:       float
    src_bal:      float
    src_new_bal:  float
    dst_bal:      float
    dst_new_bal:  float
    day_of_month: int # Day of the month (~1-30)
    hour_of_day:  int # Hour of the day (~0-23)

class Prediction(BaseModel):
    """
    This data model represents the prediction result.
    """
    pred:       bool # Prediction result (fraudulent or not)
    pred_proba: Optional[float] = None # Probability of being fraudulent (if available)

class Output(Transaction, Prediction):
    """
    This data model represent a row in the table where the predictions are saved.
    It combines the Transaction and Prediction models.
    It includes all fields from Transaction and Prediction, along with metadata.
    The metadata includes:
    - timestamp: The time when the prediction was made.
    - model_version: The version of the model used for prediction.
    - scaler_version: The version of the scaler used for preprocessing.
    """
    timestamp:      str # Timestamp when the prediction was made
    model_version:  str # Version of the model used for prediction
    scaler_version: str # Version of the scaler used for preprocessing

def preprocess_data(X: Transaction)->Features:
    """
    This function preprocesses the input data for the model, 
    following insights from the EDA.
    """
    # This mapping must be consistent with the model training phase.
    transac_type_map = {
        'TRANSFER': 1,
        'CASH_OUT': 0,
    }
    return Features(
        transac_type=transac_type_map.get(X.transac_type, -1),
        amount=X.amount,
        src_bal=X.src_bal,
        src_new_bal=X.src_new_bal,
        dst_bal=X.dst_bal,
        dst_new_bal=X.dst_new_bal,
        day_of_month=(X.time_ind // 24) + 1,
        hour_of_day=X.time_ind % 24
    )

def save_result(prediction: Prediction, transaction: Transaction):
    """
    This function saves the prediction result to the database.
    It creates an Output object that combines the transaction and prediction data,
    along with metadata: timestamp, model version, and scaler version.
    Args:
        prediction (Prediction): The prediction result containing pred and pred_proba.
        transaction (Transaction): The transaction data containing all relevant fields.
    Returns:
        None
    """
    engine = create_engine(config.db_url)
    dat = Output(
        **transaction.model_dump(),
        **prediction.model_dump(),
        # add metadata
        timestamp=datetime.now().isoformat(),
        model_version=config.model_path,
        scaler_version=config.scaler_path
    ).model_dump()

    df = pd.DataFrame([dat])
    df.to_sql(config.dst_table_name, con=engine, if_exists='append', index=False)
    print(f"Saved prediction to {config.dst_table_name} table in the database.")

def get_all_fraud_transactions(proba_threshold: float = None) -> List[Output]:
    """
    This function retrieves predicted feaudulent transactions.
    - If `proba_threshold` is provided, it filters transactions based on the predicted probability.
    - If no `proba_threshold`, it retrieves all transactions predicted as fraudulent, according to the model.
    - If no transactions are found, it returns an empty list.
    Args:
        proba_threshold (float, optional): The probability threshold for filtering transactions. Defaults to None.
    Returns:
        List[Output]: A list of Output objects representing the transactions.
        If no transactions are found, an empty list is returned.
    """
    engine = create_engine(config.db_url)
    if isinstance(proba_threshold, float):
        query = f"SELECT * FROM {config.dst_table_name} WHERE pred_proba >= {proba_threshold}"
    else:
        query = f"SELECT * FROM {config.dst_table_name} WHERE pred = True"
    df = pd.read_sql(query, engine)
    if df.empty:
        print("No transactions found.")
        return []
    return [Output(**row) for row in df.to_dict(orient='records')]
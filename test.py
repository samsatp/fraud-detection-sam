from fastapi.testclient import TestClient
from .main import app, Transaction, Prediction
from .utils import save_result
import duckdb

client = TestClient(app)

def test_predict():
    """
    [POST /predict] Should return a json consisting of 'pred'.
    """
    sample = duckdb.query("SELECT * FROM 'data/fraud_mock.csv' LIMIT 1").fetchdf().to_dict('records')[0]
    body = Transaction(**sample)
    body.is_fraud = None  # Ensure is_fraud is not set, as it should be predicted
    body.is_flagged_fraud = None  # Ensure is_flagged_fraud is not set
    with TestClient(app) as client:
        response = client.post("/predict", json=body.model_dump())
        assert response.status_code == 200
        print(response.json())
        assert response.json()['pred'] in [True, False]

def test_predict_not_fraud():
    """
    [POST /predict] If transac_type is not a 'TRANSFER' or 'CASH_OUT', it should not be fraudulent.
    """
    sample = duckdb.query("SELECT * FROM 'data/fraud_mock.csv' LIMIT 1").fetchdf().to_dict('records')[0]
    body = Transaction(**sample)
    body.transac_type = "DEBIT"
    body.is_fraud = None  # Ensure is_fraud is not set, as it should be predicted
    body.is_flagged_fraud = None  # Ensure is_flagged_fraud is not set
    with TestClient(app) as client:
        response = client.post("/predict", json=body.model_dump())
        assert response.status_code == 200
        print(response.json())
        assert response.json()['pred'] is False

def test_get_fraud_predictions():
    """
    [GET /frauds] Should return a list of fraud predictions.
    """
    sample = duckdb.query("SELECT * FROM 'data/fraud_mock.csv' LIMIT 1").fetchdf().to_dict('records')[0]
    transaction = Transaction(**sample)
    prediction = Prediction(pred=True, pred_proba=0.95)
    save_result(prediction, transaction)  # Save a dummy postive prediction

    with TestClient(app) as client:
        response = client.get("/frauds")
        assert response.status_code == 200
        print(response.json())
        assert isinstance(response.json(), list)
        if response.json():
            assert 'pred' in response.json()[0]
            assert 'pred_proba' in response.json()[0]
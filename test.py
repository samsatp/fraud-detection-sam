from fastapi.testclient import TestClient
from main import app, Transaction, Prediction
from config import config
import duckdb

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    print(response.json())
    assert response.json() == config.model_path

def test_predict():
    sample = duckdb.query("SELECT * FROM 'data/fraud_mock.csv' LIMIT 1").fetchdf().to_dict('records')[0]
    body = Transaction(**sample)
    with TestClient(app) as client:
        response = client.post("/predict", json=body.model_dump())
        assert response.status_code == 200
        print(response.json())
        assert response.json()['is_fraud'] in [True, False]
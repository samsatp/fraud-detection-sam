# Fraud Detection FastAPI Service

This project is a FastAPI-based web service for detecting fraudulent financial transactions using a pre-trained machine learning model. It provides RESTful endpoints for predicting fraud and retrieving previously predicted fraudulent transactions.

## Features

- **/predict**: Accepts transaction data and returns a fraud prediction.
- **/frauds**: Returns all transactions previously predicted as fraudulent.
- Loads a pre-trained model and scaler at startup.
- Stores and retrieves predictions from a local database.
- Includes unit tests for API endpoints.

## Project Structure

```
.
├── config.py           # Configuration (paths, settings)
├── main.py             # FastAPI app and endpoints
├── utils.py            # Data preprocessing, models, helpers
├── test.py             # Unit tests for API endpoints
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker container setup
├── run_docker.sh       # Helper script to run Docker
├── data/               # Data file
├── models/             # Saved ML model and scaler
└── README.md           # Project documentation
```

## Requirements

- Python 3.10+
- Docker (optional)


## Running the FastAPI App


### With Docker

1. **Build the Docker image:**
   ```sh
   docker build -t fraud-api-sam .
   ```

2. **Run the container:**
   ```sh
   docker run -p 80:80 fraud-api-sam
   ```

Or using the provided script:
```sh
bash run_docker.sh
```
- The API will be available at [http://localhost:80](http://localhost:80)
- The documentation can be accessed at [http://localhost:80/docs](http://localhost:80/docs)

### With Python's virtual environment

1. **Create a Python3.10 venv**
    ```sh
    python3.10 -m venv .venv
    source venv/bin/activate
    ```
2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Run the FastAPI app:**
    ```sh
    uvicorn main:app --reload
    ```

- The API will be available at [http://localhost:80](http://localhost:80)
- The documentation can be accessed at [http://localhost:80/docs](http://localhost:80/docs)


## API Endpoints

### POST `/predict`

Predict if a transaction is fraudulent.

**Request Body Example:**
```json

```

**Response Example:**
```json
{
  "pred": true,
  "pred_proba": 0.98
}
```

### GET `/frauds`

Retrieve all transactions previously predicted as fraudulent.

**Query Parameters:**
- `proba_threshold` (optional): Only return frauds with probability above this threshold.

**Response Example:**
```json

```

## Testing

Run all tests using:

```sh
bash test.sh
```

Or directly with pytest:

```sh
db_url='sqlite:///test.db' pytest test.py -svv
```

## Configuration

To adjust configuration, modify the `config.py` file or override with a `.env` file.

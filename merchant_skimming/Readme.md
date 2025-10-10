# Digital Skimming Detection Module (SENTRI+)

This package implements a modular, merchant-side digital skimming detection engine as described in the SENTRI+ architecture. It analyzes merchant websites and client-side telemetry to score the risk of digital skimming attacks (malicious JavaScript injections, data exfiltration, etc.) using static and dynamic analysis, with support for XGBoost-based risk scoring.

## Features

- **Static analysis** of merchant web pages for suspicious scripts and behaviors
- **Dynamic analysis** using HAR files or RUM logs for evidence of exfiltration
- **Risk scoring** (0–9) per merchant, using XGBoost or rule-based fallback
- **Lookup table output**: `merchant_id` → `risk_score`
- **Configurable allowlists and script baselines**
- **Explainable output** (top signals and suspicious domains)
- **Container-ready** (see Dockerfile)

## Installation

1. Clone or download the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt

3. Run in static mode (no HAR):
python -m skimming_detection.cli \
  --catalog merchants.xml \
  --out risk_scores.xml

4. With HAR/RUM evidence:
python -m skimming_detection.cli \
  --catalog merchants.xml \
  --har-dir ./har \
  --rum ./rum_events.jsonl \
  --with-explanations \
  --out risk_scores_explained.xml

## XGBoost Model Training and Updating

This module supports training an XGBoost classifier for merchant skimming risk detection using your available merchant database.

### Training Workflow

1. **Prepare Training Data**
   - Format your merchant skimming dataset as a CSV file with relevant features and target labels.
   - Perform any necessary data cleaning and feature engineering.

2. **Train the XGBoost Model**
   - Use the provided training script or notebook to fit an XGBoost model on your merchant skimming data.
   - The script will handle feature selection, model fitting, and evaluation (recommended metric: AUC-PR).

3. **Export the Model in JSON Format**
   - After successful training and validation, export the trained model to JSON format:
     ```python
     best_model.save_model("skimming_xgb.json")
     ```

4. **Update the Production Model**
   - Replace the existing model file in the `models` directory with your newly trained model:
     ```bash
     mv skimming_xgb.json models/skimming_xgb.json
     ```
   - Ensure the new model passes all validation and integration tests before deploying to production.

5. **Model Usage**
   - The updated `skimming_xgb.json` will be automatically loaded by the detection pipeline for merchant skimming analysis.
   - For inference, ensure input features are aligned with the training feature order.

**Best Practices:**
- Maintain version history of trained models for traceability and rollback.
- Validate model performance on a holdout set before replacing the production model.
- Backup the previous model before overwriting to ensure recoverability.
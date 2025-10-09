import numpy as np
import pandas as pd
from xgboost import XGBClassifier
import warnings
warnings.filterwarnings("ignore")

def get_vulnerability_score(card):
    
    return 0.1, 0.2, 0.3, 0.4, 0.5
#     return risk_score1, risk_score2, risk_score3, risk_score4, risk_score5

def get_merch_risk_score(merchant):
    
    return 7
#     return merch_risk_score
def score_transaction(card, merchant, amount, mcc, hour_of_day):
    star_score = 1
    explanation_string = ""
    
    risk_score1, risk_score2, risk_score3, risk_score4, risk_score5 = get_vulnerability_score(card)
    merch_risk_score = get_merch_risk_score(merchant)
    col_names = ['mcc', 'hour_of_day', 'amount', 'vulnerability_score1',
       'vulnerability_score2', 'vulnerability_score3', 'vulnerability_score4',
       'vulnerability_score5', 'merch_risk_score']
    col_dtypes = {'mcc' : int, 'hour_of_day' : int, 'amount' : float, 'vulnerability_score1' : float,
       'vulnerability_score2' : float, 'vulnerability_score3' : float, 'vulnerability_score4' : float,
       'vulnerability_score5' : float, 'merch_risk_score' : int}
    
    df = pd.DataFrame(columns=col_names).astype(col_dtypes)
    df["hour_of_day"] = [hour_of_day]
    df["mcc"][0] = int(mcc)
    df["amount"][0] = float(amount)
    df["vulnerability_score1"][0] = float(risk_score1)
    df["vulnerability_score2"][0] = float(risk_score2)
    df["vulnerability_score3"][0] = float(risk_score3)
    df["vulnerability_score4"][0] = float(risk_score4)
    df["vulnerability_score5"][0] = float(risk_score5)
    df["merch_risk_score"][0] = int(merch_risk_score)
    
    xgbc = XGBClassifier()
    xgbc.load_model("xgboost_model_sentri.json")
    
    probs = xgbc.predict_proba(df)
    
    df["score"] = probs[:, 1]
    
    prob_score = df["score"][0]
    
    if prob_score >= 0.8:
        star_score = 1
    elif prob_score >= 0.6:
        star_score = 2
    elif prob_score >= 0.4:
        star_score = 3
    elif prob_score >= 0.2:
        star_score = 4
    elif prob_score >= 0:
        star_score = 5
        
    cb_file = pd.read_excel("chargeback_file.xlsx")
    fraud_file = pd.read_excel("fraud_file.xlsx")
    
    cb_score = cb_file[cb_file["card"] == card].reset_index(drop=True)["cb_score"][0]
    fraud_score = fraud_file[fraud_file["card"] == card].reset_index(drop=True)["fraud_score"][0]
    
    if cb_score > 0.4 and fraud_score > 0.4:
        explanation_string = "High Fraud, High Chargeback"
    elif cb_score <= 0.4 and fraud_score > 0.4:
        explanation_string = "High Fraud, Low Chargeback"
    if cb_score > 0.4 and fraud_score <= 0.4:
        explanation_string = "Low Fraud, High Chargeback"
    if cb_score <= 0.4 and fraud_score <= 0.4:
        explanation_string = "Low Fraud, Low Chargeback"
    
    if max(risk_score1, risk_score2, risk_score3, risk_score4, risk_score5) >= 0.9:
        return 1, "Suspicious Call/Message Activity"
    
    return star_score, explanation_string


score_transaction(0, 4060646732831064559, 4.29, 5411, 12)
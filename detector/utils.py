"""
Loads the SVM model + TF-IDF vectorizer you already trained in Colab
(svm_model.pkl, tfidf_vectorizer.pkl) and runs predictions on
submitted assignment files.

Drop your two .pkl files into the ml_models/ folder at the project
root — see ml_models/README.txt for exact instructions. Nothing here
retrains or recreates the model; it only loads what you already saved.
"""
import os

import joblib
import numpy as np
from django.conf import settings

_MODEL = None
_VECTORIZER = None


def _load_model_and_vectorizer():
    global _MODEL, _VECTORIZER
    if _MODEL is None or _VECTORIZER is None:
        model_path = os.path.join(settings.ML_MODELS_DIR, 'svm_model.pkl')
        vectorizer_path = os.path.join(settings.ML_MODELS_DIR, 'tfidf_vectorizer.pkl')

        if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
            raise FileNotFoundError(
                'svm_model.pkl / tfidf_vectorizer.pkl not found in ml_models/. '
                'Copy the two files you saved from Colab into that folder.'
            )
        _MODEL = joblib.load(model_path)
        _VECTORIZER = joblib.load(vectorizer_path)
    return _MODEL, _VECTORIZER


def extract_text(file_field):
    """Extract raw text from an uploaded .txt, .docx, or .pdf file."""
    name = file_field.name.lower()
    file_field.open('rb')
    file_field.seek(0)

    if name.endswith('.txt'):
        raw = file_field.read()
        return raw.decode('utf-8', errors='ignore')

    if name.endswith('.docx'):
        import docx
        document = docx.Document(file_field)
        return '\n'.join(p.text for p in document.paragraphs)

    if name.endswith('.pdf'):
        from PyPDF2 import PdfReader
        reader = PdfReader(file_field)
        return '\n'.join((page.extract_text() or '') for page in reader.pages)

    raise ValueError('Unsupported file type. Please upload a .txt, .docx, or .pdf file.')


def explain(text, top_n=8):
    """
    Explainable-AI breakdown of a single prediction.

    Because the model is a *linear* SVM over TF-IDF features, its decision
    score is literally a sum of (word's TF-IDF value x that word's learned
    weight) across every word in the text. That means we can read off the
    exact words driving a prediction — no LIME/SHAP approximation needed,
    just the model's own arithmetic. Deep learning models don't offer this
    for free, which is one of the practical benefits of the TF-IDF + linear
    SVM approach used in this project.

    Returns two lists of (word, contribution_score), sorted by strength:
      - top words pushing the prediction toward "AI-generated"
      - top words pushing the prediction toward "Human-written"
    """
    model, vectorizer = _load_model_and_vectorizer()

    if not hasattr(model, 'coef_'):
        # Model isn't linear (e.g. RandomForest/XGBoost) — no per-word
        # coefficient explanation is available for those out of the box.
        return [], []

    X = vectorizer.transform([text])
    coef = model.coef_
    coef = coef.toarray()[0] if hasattr(coef, 'toarray') else np.asarray(coef).ravel()
    feature_names = vectorizer.get_feature_names_out()

    row = X.tocoo()
    contributions = [
        (feature_names[idx], float(tfidf_val) * float(coef[idx]))
        for idx, tfidf_val in zip(row.col, row.data)
    ]
    contributions.sort(key=lambda item: item[1], reverse=True)

    top_ai = [c for c in contributions if c[1] > 0][:top_n]
    top_human = sorted(
        [c for c in contributions if c[1] < 0], key=lambda item: item[1]
    )[:top_n]

    return top_ai, top_human


def predict(text):
    """
    Returns predicted label, an approximate AI/Human confidence split, and
    an explainability breakdown of the top contributing words.

    Note: LinearSVC (your final model) has no predict_proba — it only
    gives a decision_function margin. We pass that margin through a
    sigmoid to get a 0-100 scale suitable for the chart. This is a
    distance-based approximation, not a calibrated probability. If you
    later swap in a model trained with probability=True (SVC) or
    CalibratedClassifierCV, predict_proba will be used automatically.
    """
    model, vectorizer = _load_model_and_vectorizer()
    X = vectorizer.transform([text])
    pred = model.predict(X)[0]

    if hasattr(model, 'predict_proba'):
        proba = model.predict_proba(X)[0]
        ai_confidence = float(proba[1]) * 100
    else:
        margin = model.decision_function(X)[0]
        ai_confidence = float(1 / (1 + np.exp(-margin))) * 100

    human_confidence = 100 - ai_confidence
    label = 'AI-generated' if pred == 1 else 'Human-written'

    top_ai_terms, top_human_terms = explain(text)

    return {
        'label': label,
        'ai_probability': round(ai_confidence, 2),
        'human_probability': round(human_confidence, 2),
        'top_ai_terms': top_ai_terms,
        'top_human_terms': top_human_terms,
    }

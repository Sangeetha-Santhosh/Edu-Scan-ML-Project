Place your two Colab-trained files directly in this folder:

    ml_models/svm_model.pkl
    ml_models/tfidf_vectorizer.pkl

These are the exact files you created with:
    joblib.dump(svm_model, 'svm_model.pkl')
    joblib.dump(tfidf, 'tfidf_vectorizer.pkl')

Nothing in this project retrains or recreates them - detector/utils.py
just loads them with joblib and reuses them as-is.

# AI-Generated Assignment Detection System — Django Web App

## Setup

1. Create a virtual environment and install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Copy your trained model files from Colab into `ml_models/`:
   ```
   ml_models/svm_model.pkl
   ml_models/tfidf_vectorizer.pkl
   ```
   (See ml_models/README.txt.)

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Create a teacher account (the only way to log in as a teacher — there's
   no public signup for teachers):
   ```
   python manage.py createsuperuser
   ```
   When prompted, use any username/password. After creation, open
   `python manage.py shell` and run:
   ```python
   from accounts.models import User
   u = User.objects.get(username='<the username you just created>')
   u.role = 'TEACHER'
   u.save()
   ```
   (Or just set `role='TEACHER'` directly when creating the user — see the
   chat instructions for a one-line shell command.)

5. Run the server:
   ```
   python manage.py runserver
   ```

6. Visit http://127.0.0.1:8000/
   - Teacher logs in with username/password at "Teacher Login"
   - Teacher adds students (name, register number, date of birth) — no
     password is created for students
   - Teacher creates an assignment and selects which students receive it
   - Student logs in at "Student Login" using register number + DOB
   - Student uploads their submission (.txt, .docx, or .pdf)
   - Teacher opens the assignment, downloads the submission, and clicks
     "Check for AI" to run it through the saved SVM + TF-IDF model and see
     an AI vs Human confidence chart

## Project layout

- `accounts/` — custom User model (role: TEACHER/STUDENT), teacher login
  (username+password), student login (reg number+DOB via a custom auth
  backend), logout
- `assignments/` — StudentProfile, Assignment, Submission models; teacher
  dashboard, add-student, create-assignment, submission download, and
  student dashboard/submission views
- `detector/` — loads `ml_models/svm_model.pkl` + `ml_models/tfidf_vectorizer.pkl`,
  extracts text from uploaded .txt/.docx/.pdf files, predicts, and renders
  the result with a Chart.js doughnut chart

## Notes on the AI confidence score

Your final model is a `LinearSVC`, which does not expose `predict_proba`
(only SVC with `probability=True` does). `detector/utils.py` passes the
model's `decision_function` margin through a sigmoid to produce a 0–100%
scale for the chart. This is a reasonable approximation for display
purposes but is not a calibrated probability — worth a one-line caveat
in your report if you present the percentage as "confidence."

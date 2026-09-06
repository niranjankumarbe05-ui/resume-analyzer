from flask import Flask, render_template, request
import os
import PyPDF2

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# 📄 Extract text from PDF
def extract_text(file_path):
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text


# 🧠 Smart Resume Analysis (NO API)
def analyze_resume(text):
    text_lower = text.lower()

    skills_db = [
        "python", "java", "sql", "machine learning",
        "flask", "html", "css", "javascript", "react"
    ]

    found_skills = [s for s in skills_db if s in text_lower]

    # 📊 Realistic scoring
    skills_score = min(len(found_skills) * 10, 40)

    content_score = 30 if len(text) > 1000 else 15
    formatting_score = 20 if "\n" in text else 10

    total_score = skills_score + content_score + formatting_score
    total_score = min(total_score, 100)

    # Missing things
    missing = []
    if "certification" not in text_lower:
        missing.append("Certifications")
    if "linkedin" not in text_lower:
        missing.append("LinkedIn Profile")

    # Issues
    issues = []
    if len(text) < 800:
        issues.append("Resume content too short")
    if "project" not in text_lower:
        issues.append("No projects mentioned")

    return {
        "score": total_score,
        "skills": found_skills,
        "missing": missing,
        "issues": issues,
        "formatting": formatting_score,
        "content": content_score,
        "skills_score": skills_score
    }


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["resume"]

        if file:
            path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(path)

            text = extract_text(path)
            result = analyze_resume(text)

            return render_template("index.html", result=result)

    return render_template("index.html", result=None)


if __name__ == "__main__":
    app.run(debug=True)
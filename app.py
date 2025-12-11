from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from models import db, User, Job, Application
import requests
import re

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///job.db"
db.init_app(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for("register"))
        password_hash = generate_password_hash(password)
        user = User(username=username, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        return redirect(url_for("index"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            if user.role == 'employer':
                return redirect(url_for("employer_dashboard"))
            else:
                return redirect(url_for("job_seeker_dashboard"))
        flash("Invalid credentials")
        return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/employer_dashboard")
@login_required
def employer_dashboard():
    user = User.query.get(session["user_id"])
    if not user:
        return redirect(url_for("login"))
    jobs = Job.query.filter_by(user_id=user.id).order_by(Job.date_posted.desc()).all()
    return render_template("employer_dashboard.html", jobs=jobs)

@app.route("/job_seeker_dashboard")
def job_seeker_dashboard():
    jobs = Job.query.order_by(Job.date_posted.desc()).all()
    applied_job_ids = set()
    if "user_id" in session:
        applications = Application.query.filter_by(user_id=session["user_id"]).all()
        applied_job_ids = {app.job_id for app in applications}
    return render_template("job_seeker_dashboard.html", jobs=jobs, applied_job_ids=applied_job_ids)

@app.route("/apply/<int:job_id>", methods=["GET", "POST"])
@login_required
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)
    # Check if already applied
    existing = Application.query.filter_by(user_id=session["user_id"], job_id=job_id).first()
    if request.method == "POST":
        if existing:
            flash("You have already applied for this job.")
            return redirect(url_for("job_seeker_dashboard"))
        resume_text = request.form.get("resume_text", "")
        application = Application(user_id=session["user_id"], job_id=job_id, resume_text=resume_text)
        db.session.add(application)
        db.session.commit()
        flash("Application submitted successfully!")
        return redirect(url_for("job_seeker_dashboard"))
    return render_template("apply.html", job=job, existing_application=existing)

@app.route("/withdraw/<int:job_id>")
@login_required
def withdraw_application(job_id):
    application = Application.query.filter_by(user_id=session["user_id"], job_id=job_id).first()
    if not application:
        flash("You have not applied for this job.")
        return redirect(url_for("job_seeker_dashboard"))
    db.session.delete(application)
    db.session.commit()
    flash("Application withdrawn successfully!")
    return redirect(url_for("job_seeker_dashboard"))

@app.route("/add_job", methods=["GET", "POST"])
@login_required
def add_job():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form.get("description", "")
        company = request.form["company"]
        location = request.form["location"]
        salary = request.form.get("salary", "")
        user_id = session["user_id"]
        job = Job(title=title, description=description, company=company, location=location, salary=salary, user_id=user_id)
        db.session.add(job)
        # Set role to employer
        user = User.query.get(user_id)
        user.role = 'employer'
        db.session.commit()
        return redirect(url_for("employer_dashboard"))
    return render_template("add_job.html")

@app.route("/edit_job/<int:id>", methods=["GET", "POST"])
@login_required
def edit_job(id):
    job = Job.query.get_or_404(id)
    if job.user_id != session["user_id"]:
        return redirect(url_for("index"))
    if request.method == "POST":
        job.title = request.form["title"]
        job.description = request.form.get("description", "")
        job.company = request.form["company"]
        job.location = request.form["location"]
        job.salary = request.form.get("salary", "")
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("edit_job.html", job=job)

@app.route("/delete_job/<int:id>")
@login_required
def delete_job(id):
    job = Job.query.get_or_404(id)
    if job.user_id != session["user_id"]:
        return redirect(url_for("index"))
    db.session.delete(job)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/chat", methods=["GET", "POST"])
@login_required
def chat():
    response = None
    if request.method == "POST":
        message = request.form["message"]
        # Send to Ollama
        payload = {
            "model": "gemma:2b",
            "prompt": f"You are an AI assistant for JobConnect job board. User message: {message}\n\nAnalyze the user message. If it indicates creating a job, respond ONLY with: CREATE_JOB: title|description|company|location|salary\nIf it indicates editing a job, respond ONLY with: EDIT_JOB: id|title|description|company|location|salary\nIf it indicates deleting a job (e.g., 'delete job ID 1'), respond ONLY with: DELETE_JOB: id\n\nIf none of these, respond helpfully. Do not add extra text to commands.",
            "stream": False
        }
        try:
            print(f"Sending to Ollama: {payload}")
            ollama_response = requests.post("http://localhost:11434/api/generate", json=payload)
            print(f"Ollama status: {ollama_response.status_code}")
            if ollama_response.status_code == 200:
                ai_data = ollama_response.json()
                ai_text = ai_data.get("response", "")
                print(f"AI response: {ai_text}")
                response = ai_text
                # Parse commands
                if "CREATE_JOB:" in ai_text:
                    parts = ai_text.split("CREATE_JOB:")[1].split("\n")[0].strip().split("|")
                    if len(parts) >= 5:
                        job = Job(title=parts[0].strip(), description=parts[1].strip(), company=parts[2].strip(), location=parts[3].strip(), salary=parts[4].strip(), user_id=session["user_id"])
                        db.session.add(job)
                        db.session.commit()
                        response += "\n✅ Job created successfully!"
                elif "EDIT_JOB:" in ai_text:
                    parts = ai_text.split("EDIT_JOB:")[1].split("\n")[0].strip().split("|")
                    if len(parts) >= 6:
                        job_id = int(parts[0].strip())
                        job = Job.query.get(job_id)
                        if job and job.user_id == session["user_id"]:
                            job.title = parts[1].strip()
                            job.description = parts[2].strip()
                            job.company = parts[3].strip()
                            job.location = parts[4].strip()
                            job.salary = parts[5].strip()
                            db.session.commit()
                            response += "\n✅ Job updated successfully!"
                elif "DELETE_JOB:" in ai_text:
                    match = re.search(r'DELETE_JOB:\s*(\d+)', ai_text)
                    if match:
                        job_id = int(match.group(1))
                        job = Job.query.get(job_id)
                        if job and job.user_id == session["user_id"]:
                            db.session.delete(job)
                            db.session.commit()
                            response += "\n✅ Job deleted successfully!"
                        else:
                            response += "\n❌ Job not found or you don't have permission to delete it."
                    else:
                        response += "\n❌ Could not parse job ID for deletion."
            else:
                response = f"AI error: {ollama_response.text}"
        except Exception as e:
            print(f"Exception: {e}")
            response = f"AI assistant unavailable: {str(e)}"
    return render_template("chat.html", response=response)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

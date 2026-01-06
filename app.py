from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from flask_wtf import CSRFProtect
from models import db, User, Job, Application
import requests
import re
import logging
import os

def check_ollama():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "your_secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///job.db")
app.config['UPLOAD_FOLDER'] = 'uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
db.init_app(app)
csrf = CSRFProtect(app)

with app.app_context():
    db.create_all()

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        username = request.form["username"].strip()
        password = request.form["password"]
        if len(username) < 3:
            flash("Username must be at least 3 characters long")
            return redirect(url_for("register"))
        if len(password) < 6:
            flash("Password must be at least 6 characters long")
            return redirect(url_for("register"))
        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for("register"))
        password_hash = generate_password_hash(password)
        user = User(username=username, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        session["user_id"] = user.id
        session["is_admin"] = (user.username == 'admin')
        return redirect(url_for("index"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["is_admin"] = (user.username == 'admin')
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

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = db.session.get(User, session["user_id"])
    if request.method == "POST":
        user.bio = request.form.get("bio", "")
        user.contact_email = request.form.get("contact_email", "")
        user.phone = request.form.get("phone", "")
        user.linkedin = request.form.get("linkedin", "")
        db.session.commit()
        flash("Profile updated successfully")
        return redirect(url_for("profile"))
    return render_template("profile.html", user=user)

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/admin")
@login_required
def admin_dashboard():
    user = db.session.get(User, session["user_id"])
    if user.username != 'admin':
        return redirect(url_for('index'))
    users = User.query.all()
    jobs = Job.query.all()
    applications = Application.query.all()

    # Analytics
    from sqlalchemy import func
    job_categories = db.session.query(Job.category, func.count(Job.id)).group_by(Job.category).all()
    app_categories = db.session.query(Job.category, func.count(Application.id)).join(Application.job).group_by(Job.category).all()
    top_companies = db.session.query(Job.company, func.count(Application.id)).join(Application.job).group_by(Job.company).order_by(func.count(Application.id).desc()).limit(5).all()
    employer_count = User.query.filter_by(role='employer').count()
    job_seeker_count = User.query.filter_by(role='job_seeker').count() + User.query.filter_by(role='employee').count()  # assuming employee is job_seeker

    analytics = {
        'job_categories': dict(job_categories),
        'app_categories': dict(app_categories),
        'top_companies': top_companies,
        'employer_count': employer_count,
        'job_seeker_count': job_seeker_count
    }

    return render_template("admin.html", users=users, jobs=jobs, applications=applications, analytics=analytics)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/employer_dashboard")
@login_required
def employer_dashboard():
    user = db.session.get(User, session["user_id"])
    if not user:
        return redirect(url_for("login"))
    jobs = Job.query.filter_by(user_id=user.id).order_by(Job.date_posted.desc()).all()
    return render_template("employer_dashboard.html", jobs=jobs)

@app.route("/job_seeker_dashboard")
def job_seeker_dashboard():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    location = request.args.get('location', '').strip()
    salary_min = request.args.get('salary_min', '').strip()
    salary_max = request.args.get('salary_max', '').strip()

    job_query = Job.query.order_by(Job.date_posted.desc())

    if query:
        job_query = job_query.filter(
            (Job.title.contains(query)) | (Job.description.contains(query)) | (Job.company.contains(query)) | (Job.location.contains(query)) | (Job.category.contains(query))
        )
    if category:
        job_query = job_query.filter(Job.category == category)
    if location:
        job_query = job_query.filter(Job.location.contains(location))
    if salary_min:
        # Assuming salary is like "$50,000 - $70,000", extract numbers
        try:
            min_val = int(salary_min.replace('$', '').replace(',', '').split('-')[0].strip())
            job_query = job_query.filter(Job.salary.contains(str(min_val)))
        except:
            pass
    if salary_max:
        try:
            max_val = int(salary_max.replace('$', '').replace(',', '').split('-')[-1].strip())
            job_query = job_query.filter(Job.salary.contains(str(max_val)))
        except:
            pass

    jobs_pagination = job_query.paginate(page=page, per_page=10, error_out=False)
    applied_job_ids = set()
    recommended_jobs = []
    if "user_id" in session:
        applications = Application.query.filter_by(user_id=session["user_id"]).all()
        applied_job_ids = {app.job_id for app in applications}

        # Recommendations based on applied categories
        applied_categories = set()
        for app in applications:
            if app.job.category:
                applied_categories.add(app.job.category)

        if applied_categories:
            recommended_jobs = Job.query.filter(
                Job.category.in_(applied_categories),
                ~Job.id.in_(applied_job_ids)
            ).limit(5).all()

    return render_template("job_seeker_dashboard.html", jobs_pagination=jobs_pagination, applied_job_ids=applied_job_ids, query=query, category=category, location=location, salary_min=salary_min, salary_max=salary_max, recommended_jobs=recommended_jobs)

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
        if 'resume_file' in request.files:
            file = request.files['resume_file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                application.resume_file = filename
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
        category = request.form.get("category", "")
        user_id = session["user_id"]
        job = Job(title=title, description=description, company=company, location=location, salary=salary, category=category, user_id=user_id)
        db.session.add(job)
        # Set role to employer
        user = db.session.get(User, user_id)
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
        job.category = request.form.get("category", "")
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
        logging.info(f"Chat request from user {session.get('user_id')}: {message}")
        if not check_ollama():
            response = "AI assistant is currently unavailable. Please ensure Ollama is running with the gemma:2b model."
        else:
            # Send to Ollama
            payload = {
                "model": "gemma:2b",
                "prompt": f"You are an AI assistant for JobConnect job board. User message: {message}\n\nAnalyze the user message. If it indicates creating a job, respond ONLY with: CREATE_JOB: title|description|company|location|salary\nIf it indicates editing a job, respond ONLY with: EDIT_JOB: id|title|description|company|location|salary\nIf it indicates deleting a job (e.g., 'delete job ID 1'), respond ONLY with: DELETE_JOB: id\n\nIf none of these, respond helpfully. Do not add extra text to commands.",
                "stream": False
            }
            try:
                logging.info(f"Sending payload to Ollama: {payload}")
                ollama_response = requests.post("http://localhost:11434/api/generate", json=payload)
                logging.info(f"Ollama response status: {ollama_response.status_code}")
                if ollama_response.status_code == 200:
                    ai_data = ollama_response.json()
                    ai_text = ai_data.get("response", "")
                    logging.info(f"AI text: {ai_text}")
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
                            job = db.session.get(Job, job_id)
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
                            job = db.session.get(Job, job_id)
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
                logging.error(f"Exception in chat: {e}")
                response = f"AI assistant unavailable: {str(e)}"
    return render_template("chat.html", response=response)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

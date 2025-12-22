# JobConnect

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-red.svg)](https://flask.palletsprojects.com/)

A comprehensive full-stack job board application built with Flask, SQLAlchemy, and integrated AI assistance for seamless job management and career guidance.

## 🌟 Features

### 👨‍💼 For Job Seekers
- **Browse Jobs**: Explore available job listings with advanced filtering
- **Easy Applications**: Apply to jobs with resume upload functionality
- **Application Management**: View and withdraw submitted applications
- **AI Career Assistant**: Get personalized career advice and job recommendations
- **Profile Management**: Update personal information and preferences

### 🏢 For Employers
- **Job Posting**: Create and publish new job opportunities
- **Job Management**: Edit, update, or delete existing job listings
- **Application Review**: View and manage job applications (future enhancement)
- **AI Job Creation**: Use natural language commands to create job postings
- **Dashboard Analytics**: Monitor job performance and applicant statistics

### 🤖 AI Assistant
- **Powered by Ollama**: Integrated with Gemma 2B model for intelligent interactions
- **Natural Language Processing**: Understand and execute job management commands
- **Supported Commands**:
  - `CREATE_JOB`: Generate new job postings
  - `EDIT_JOB`: Modify existing job details
  - `DELETE_JOB`: Remove job listings
- **Chat Interface**: Interactive conversation for job-related queries

### 👑 Admin Features
- **User Management**: Oversee user accounts and permissions
- **System Monitoring**: View application statistics and logs
- **Content Moderation**: Manage job postings and user content

## 🛠️ Tech Stack

- **Backend Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite (easily configurable for PostgreSQL/MySQL)
- **Frontend**: Bootstrap 5 with Jinja2 templating
- **Authentication**: Werkzeug security with password hashing
- **AI Integration**: Ollama API for local AI processing
- **File Handling**: Secure file uploads for resumes
- **Deployment**: Ready for Heroku, DigitalOcean, or any WSGI server

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Git
- Ollama (optional, for AI features)

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/mea03kkw/jobconnect_app.git
cd jobconnect_app
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up AI Features (Optional)
```bash
# Download and install Ollama from https://ollama.ai
ollama pull gemma:2b
ollama serve
```

### 5. Initialize Database
```bash
python app.py
```
The database will be automatically created on first run.

### 6. Run the Application
```bash
python app.py
```

### 7. Access the Application
Open your browser and navigate to: `http://localhost:5000`

## 📁 Project Structure

```
jobconnect_app/
├── app.py                 # Main Flask application and routes
├── models.py              # SQLAlchemy database models
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── .gitignore            # Git ignore rules
├── templates/            # Jinja2 HTML templates
│   ├── base.html         # Base template with navigation
│   ├── index.html        # Homepage
│   ├── login.html        # User login page
│   ├── register.html     # User registration page
│   ├── employer_dashboard.html  # Employer control panel
│   ├── job_seeker_dashboard.html # Job seeker dashboard
│   ├── add_job.html      # Job creation form
│   ├── edit_job.html     # Job editing form
│   ├── apply.html        # Job application form
│   ├── chat.html         # AI assistant interface
│   ├── admin.html        # Admin management panel
│   └── profile.html      # User profile management
├── static/               # Static assets
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript files
│   └── images/          # Image assets
├── uploads/             # User uploaded files (resumes)
├── docs/                # Static demo files for GitHub Pages
└── instance/            # SQLite database files
```

## 🎯 Usage Guide

### Getting Started
1. **Register**: Create a new account as either a Job Seeker or Employer
2. **Login**: Sign in with your credentials
3. **Complete Profile**: Add personal information and preferences

### For Employers
1. **Post Jobs**: Use the dashboard to create new job listings
2. **AI Assistance**: Use the chat feature with commands like "Create a software engineer position"
3. **Manage Applications**: Review incoming applications (coming soon)

### For Job Seekers
1. **Browse Jobs**: Use filters to find relevant opportunities
2. **Apply**: Submit applications with resume uploads
3. **Track Applications**: Monitor application status from your dashboard

### AI Chat Commands
- `CREATE_JOB: Create a new job posting for a Python Developer`
- `EDIT_JOB: Update job ID 123 with new requirements`
- `DELETE_JOB: Remove job ID 456`

## 🌐 Live Demo

Experience the application with mock data: [JobConnect Demo](https://mea03kkw.github.io/jobconnect_app/)

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/job.db
OLLAMA_BASE_URL=http://localhost:11434
FLASK_ENV=development
```

### Database Migration
For production deployments, consider using Flask-Migrate for database versioning.

## 🚀 Deployment

### Heroku Deployment
1. Create a Heroku app
2. Set environment variables in Heroku dashboard
3. Deploy using Heroku Git:
```bash
heroku create your-app-name
git push heroku main
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting PR

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flask framework for the robust backend
- Bootstrap for responsive UI components
- Ollama for local AI capabilities
- SQLAlchemy for database abstraction

## 📞 Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check the documentation in the `docs/` folder
- Review the demo for feature examples

---

**Happy job hunting and recruiting! 🎉**

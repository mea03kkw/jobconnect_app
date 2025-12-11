# JobConnect

A full-stack job board application built with Flask, SQLAlchemy, and AI assistance.

## Features

### For Job Seekers
- Browse available job listings
- Apply to jobs with resume submission
- View and withdraw applications
- AI-powered career assistance

### For Employers
- Post new job opportunities
- Manage job listings (edit/delete)
- View applications (future feature)
- AI assistance for job creation

### AI Assistant
- Powered by Ollama (Gemma 2B model)
- Natural language job management
- Commands: CREATE_JOB, EDIT_JOB, DELETE_JOB

## Tech Stack

- **Backend**: Flask, SQLAlchemy, SQLite
- **Frontend**: Bootstrap 5, Jinja2 templates
- **AI**: Ollama API integration
- **Authentication**: Werkzeug security

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mea03kkw/jobconnect_app.git
cd jobconnect_app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Ollama (optional, for AI features):
```bash
# Install Ollama from https://ollama.ai
ollama pull gemma:2b
ollama serve
```

4. Run the application:
```bash
python app.py
```

5. Open http://localhost:5000 in your browser

## Database

The app uses SQLite database (`instance/job.db`). The database is automatically created on first run.

## Demo

View the static demo at: [GitHub Pages Demo](https://mea03kkw.github.io/jobconnect_app/)

The demo showcases all app features with mock data.

## Project Structure

```
jobconnect_app/
├── app.py                 # Main Flask application
├── models.py              # SQLAlchemy models
├── requirements.txt       # Python dependencies
├── templates/             # Jinja2 templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── employer_dashboard.html
│   ├── job_seeker_dashboard.html
│   ├── apply.html
│   ├── add_job.html
│   ├── edit_job.html
│   └── chat.html
├── static/                # Static assets (CSS, JS, images)
├── instance/              # Database files
├── demo/                  # Static demo for GitHub Pages
└── README.md
```

## Usage

1. **Register**: Create a new account
2. **Login**: Sign in with your credentials
3. **Employer Mode**: Post jobs, manage listings
4. **Job Seeker Mode**: Browse and apply to jobs
5. **AI Chat**: Use natural language to manage jobs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).
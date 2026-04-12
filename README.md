# 🎓 CampusMind AI Platform

> 🚀 An AI-powered, role-based Academic Intelligence System for modern colleges

CampusMind is a full-stack intelligent college management system that combines data analytics, automation, and AI (RAG-based chatbot) to provide actionable insights for students, faculty, and administrators.

## 📌 Key Highlights
- 🔐 Secure Role-Based Access (Admin / Faculty / Student)
- 📊 Real-time Academic Analytics & Insights
- 🤖 AI Chatbot with Database + Document Intelligence (RAG)
- 📂 Excel-Based Data Upload System
- 📄 Automated PDF Report Generation
- 📧 Smart Email Alert System
- 📈 Department-wise Performance Tracking
- ⏰ Automated Background Scheduling (Agents)

## 🧠 Core Modules
### 🔑 Authentication System
- Secure login with session management
- Role-based dashboard routing
- Password hashing for security

### 👨‍🎓 Student Dashboard
- Latest exam result (PASS / FAIL)
- Download result as PDF
- Restricted AI access (own data only)

### 👨‍🏫 Faculty Dashboard
- Upload Students, Attendance, Marks, Exam Schedule
- Access to all student data
- Faculty AI assistant

### 🛠 Admin Dashboard
- Total students overview
- Average marks calculation
- Students at risk detection
- Department-wise attendance analytics
- Insight report generation (PDF)
- Upload and manage documents (RAG)

## 🤖 AI System (CampusMind Intelligence)
### 🔍 AI Chatbot Features
- Natural Language Query Handling
- SQL-based Answer Retrieval
- Document-based RAG (PDF search)
- Role-based data protection (Security Guard)

### 🧩 AI Architecture
- Intent Detection
- Query Routing Engine
- Database + Vector Search Integration
- Secure Response Generation

## 📊 Data Management
- 📥 Excel Upload System (via Faculty)
- 📤 Data stored in MySQL database
- 📑 Supported uploads: Students, Attendance, Marks, Exam Schedule

## 📄 Reports & Documents
- 📄 Student Result PDF Generation
- 📊 Admin Insight Report (Auto-generated)
- 📚 PDF Upload + Semantic Search (RAG)

## ⚙️ Background Automation
Using APScheduler:
- 📉 Low Attendance Detection Agent (Daily)
- 📉 Low Performance Detection Agent (Weekly)
- 📅 Exam Reminder Agent (Daily)

## 🧰 Tech Stack
### 💻 Backend
- Python (Flask)
- MySQL
- APScheduler

### 📊 Data Processing
- Pandas
- OpenPyXL

### 🤖 AI & RAG
- Sentence Transformers
- FAISS (Vector Search)
- LangChain
- Ollama (Local LLM)

### 📄 Document Processing
- PDFPlumber
- ReportLab

### 🎨 Frontend
- HTML, CSS, JavaScript
- Chart.js (Data Visualization)

## 📁 Project Structure
CampusMind/
├── app.py
├── config.py
├── requirements.txt
├── services/
│   ├── excel_service.py
│   ├── pdf_service.py
│   ├── result_pdf_service.py
│   ├── insight_service.py
│   ├── report_service.py
├── ai/
│   ├── embeddings.py
│   ├── rag_docs.py
│   ├── router.py
│   ├── intent_detector.py
│   ├── chat_guard.py
├── scheduler/
│   ├── attendance_agent.py
│   ├── performance_agent.py
│   ├── exam_reminder_agent.py
├── templates/
├── static/
├── uploads/

## 🚀 Installation & Setup
1. Clone Repository
git clone https://github.com/selvan-01/CampusMind-AI-Platform.git
cd campusmind

2. Create Virtual Environment
python -m venv venv
venv\Scripts\activate

3. Install Dependencies
pip install -r requirements.txt

4. Configure Database
- Create MySQL database: campusmind
- Update credentials in config.py

5. Run Application
python app.py

Open in browser:
http://127.0.0.1:5000

## 🔐 Security Features
- Role-based access control
- Student data protection (restricted queries)
- Password hashing
- Session management
- AI query permission guard

## ⚠️ Important Notes
- Do NOT expose config.py (contains sensitive credentials)
- Use .env for production
- Add .gitignore for security

## 📈 Future Enhancements
- AI response caching (performance boost)
- Advanced NLP intent classification
- Cloud deployment (AWS / GCP)
- Mobile app integration
- Real-time notifications

## 👨‍💻 Author
Senthamil Selvan (Sen)  
Final Year CSE Student  
AI | Data Science | AI Developer

## ⭐ Support
If you like this project:
- ⭐ Star the repository
- 🍴 Fork and contribute
- 📢 Share with others

## 📜 License
This project is developed for academic and learning purposes.

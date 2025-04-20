# 🤖 QA System using Gemini Pro API

<div align="center">

![Version](https://img.shields.io/badge/version-1.0-blue?style=flat)
![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1.0-lightgrey?style=flat&logo=flask&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini_Pro-API-orange?style=flat&logo=google&logoColor=white)
![AstraDB](https://img.shields.io/badge/AstraDB-Vector_Store-blueviolet?style=flat&logo=datastax&logoColor=white)
![LangSmith](https://img.shields.io/badge/LangSmith-Monitoring-green?style=flat)
![License](https://img.shields.io/badge/license-MIT-green?style=flat)
[![Deployment](https://img.shields.io/badge/Deployed_on-Render-purple?style=flat&logo=render&logoColor=white)](https://qa-system-using-gemini-pro-api-1.onrender.com/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=flat&logo=github&logoColor=white)](https://github.com/VisionExpo/QA-System-using-Gemini-Pro-API)

</div>

A powerful Question and Answer system built with Google's Gemini Pro API, featuring vector storage with AstraDB and LLM monitoring with LangSmith.

## ✨ Features

- 💬 **Text Q&A**: Ask questions and get detailed answers powered by Gemini Pro
- 🖼️ **Image Analysis**: Upload images for AI-powered analysis with Gemini Pro Vision
- 📄 **Document Processing**: Extract and analyze text from PDF, DOCX, and other file formats
- 🔗 **URL Processing**: Analyze content from web pages and YouTube videos
- 🔍 **Semantic Search**: Find similar content using vector embeddings
- 📊 **LLM Monitoring**: Track and analyze model performance with LangSmith
- 🗄️ **Vector Storage**: Store and retrieve vectors using AstraDB
- 🌐 **Web Interface**: Clean, responsive Flask web application

## 🚀 Tech Stack

<div align="center">

| Technology | Purpose |
|------------|---------|
| ![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat&logo=python&logoColor=white) | Core language |
| ![Flask](https://img.shields.io/badge/Flask-3.1.0-lightgrey?style=flat&logo=flask&logoColor=white) | Web framework |
| ![Gemini Pro](https://img.shields.io/badge/Gemini_Pro-API-orange?style=flat&logo=google&logoColor=white) | LLM model |
| ![AstraDB](https://img.shields.io/badge/AstraDB-Vector_Store-blueviolet?style=flat&logo=datastax&logoColor=white) | Vector database |
| ![LangSmith](https://img.shields.io/badge/LangSmith-Monitoring-green?style=flat) | LLM monitoring |
| ![Sentence Transformers](https://img.shields.io/badge/Sentence_Transformers-4.1.0-red?style=flat) | Text embeddings |
| ![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat&logo=docker&logoColor=white) | Containerization |
| ![Render](https://img.shields.io/badge/Render-Deployment-purple?style=flat&logo=render&logoColor=white) | Cloud hosting |

</div>

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Web Interface  │────▶│  Flask Backend  │────▶│   Gemini Pro    │
│                 │     │                 │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                               │
                               ▼
                 ┌─────────────────────────────┐
                 │                             │
                 │  File/URL/Image Processing  │
                 │                             │
                 └──────────────┬──────────────┘
                               │
                 ┌─────────────▼──────────────┐
                 │                            │
                 │  Sentence Transformers     │
                 │  (Vector Embeddings)       │
                 │                            │
                 └──────────────┬─────────────┘
                               │
          ┌──────────────────┐ │ ┌───────────────────┐
          │                  │ │ │                   │
          │     AstraDB      │◀┴─▶│    LangSmith      │
          │  (Vector Store)  │   │    (Monitoring)   │
          │                  │   │                   │
          └──────────────────┘   └───────────────────┘
```

## 🔧 Installation

### Prerequisites

- Python 3.10 or higher
- Google API key for Gemini Pro
- AstraDB account and token
- (Optional) LangSmith API key

### Option 1: Using Setup Scripts (Recommended) 🚀

1. Clone the repository:

   ```bash
   git clone https://github.com/VisionExpo/QA-System-using-Gemini-Pro-API.git
   cd QA-System-using-Gemini-Pro-API
   ```

2. Run the setup script:

   **For Windows:**

   ```bash
   setup_env.bat
   ```

   **For macOS/Linux:**

   ```bash
   chmod +x setup_env.sh
   ./setup_env.sh
   ```

   This script will:
   - 🔨 Create a virtual environment
   - ⚡ Activate the virtual environment
   - 📦 Install dependencies
   - 🔑 Create a `.env` file from the example if it doesn't exist

3. Edit the `.env` file and add your API keys:
   - `GOOGLE_API_KEY`: Your Google API key
   - `ASTRA_DB_TOKEN`: Your AstraDB token
   - `ASTRA_DB_ENDPOINT`: Your AstraDB endpoint
   - `LANGCHAIN_API_KEY`: (Optional) Your LangSmith API key

### Option 2: Manual Setup 🛠️

1. Clone the repository:

   ```bash
   git clone https://github.com/VisionExpo/QA-System-using-Gemini-Pro-API.git
   cd QA-System-using-Gemini-Pro-API
   ```

2. Create and activate a virtual environment:

   **For Windows:**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   **For macOS/Linux:**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables:

   ```bash
   cp .env.example .env
   ```

   Then edit the `.env` file to add your API keys.

## 🚀 Usage

### Running the Application

```bash
python app.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your web browser.

### 💬 Text Q&A Mode

Ask any question and get detailed answers from Gemini Pro:

- General knowledge questions
- Coding help
- Explanations of complex topics
- Creative writing assistance

### 🖼️ Image Analysis Mode

Upload images for AI-powered analysis:
- Object identification
- Scene description
- Text extraction from images
- Visual content analysis

### 📄 Document Processing

Upload and analyze documents:
- PDF files
- Word documents (DOCX)
- Text files
- CSV data

### 🔗 URL and YouTube Processing

Analyze content from:
- Web pages
- YouTube videos (transcripts and summaries)
- Online articles

## 🌐 Deployment

This application is deployed on Render. You can access it at:
[https://qa-system-using-gemini-pro-api-1.onrender.com/](https://qa-system-using-gemini-pro-api-1.onrender.com/)

For detailed deployment instructions, see [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md).

## 🧪 Testing

To run tests:

```bash
python -m pytest tests/
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- Google for the Gemini Pro API
- DataStax for AstraDB
- LangChain for LangSmith
- The open-source community for various libraries used in this project

## 📞 Contact

For questions or feedback, please open an issue on GitHub or contact the maintainer at gorulevishal984@gmail.com.

---

<div align="center">

Made with ❤️ by [Vishal Gorule](https://github.com/VisionExpo)

</div>

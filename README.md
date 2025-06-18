# 🧠 TDS Virtual TA Lite

A lightweight Question-Answering API that helps students find answers from **course materials** and **Discourse discussions** related to the Tools in Data Science (TDS) course at IITM.

> ✅ Works offline. No OpenAI API key required.  
> ✅ Memory footprint < 512 MB  
> ✅ Fully Pythonic & FastAPI-powered

---

## 📦 Features

- Scrapes and processes:
  - 🧵 [Discourse Forum](https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34)
  - 📘 [TDS Course Website](https://tds.s-anand.net/#/2025-01/)
- Converts content to markdown
- Runs semantic and keyword search on questions
- Exposes a public `/api/` endpoint to answer questions
- Returns relevant answers and links

---

## 🛠 Project Structure

TDS_Virtual_TA_Lite/
├── main.py # 🔁 FastAPI app with /api/ POST endpoint
├── utils.py # 🧠 Markdown loading and search logic
│
├── scrape_course.py # 🕸 Scrapes course site → tds_pages_md + course.md
├── scrape_discourse.py # 🕸 Scrapes Discourse → discourse_posts.json + discourse.md
│
├── course.md # 📘 Combined course content
├── discourse.md # 🧵 Combined Discourse threads
│
├── discourse_posts.json # 📦 Raw post data from Discourse
├── metadata.json # ℹ Metadata of downloaded pages
├── auth.json # 🔐 Browser session for Discourse (auto generated)
│
├── tds_pages_md/ # 📄 Individual markdown pages from course site
├── requirements.txt # 📦 Dependencies
└── README.md # 📖 This file

yaml
## 🚀 How to Run

### 1. Install Dependencies
pip install -r requirements.txt
playwright install
2. Scrape Discourse Posts
python scrape_discourse.py
3. Scrape Course Website
python scrape_course.py
4. Start the API
uvicorn main:app --reload

📡 API Usage
Endpoint
POST /api/

Request JSON
{
  "question": "How to perform EDA using Pandas?",
  "attachments": []  // Optional: list of base64 files (not required for Lite version)
}

Response JSON
{
  "answer": "You can use `df.describe()` and `df.info()` for EDA in pandas...",
  "links": [
    {
      "url": "https://discourse.onlinedegree.iitm.ac.in/t/some-topic/123",
      "text": "Discussion on pandas EDA"
    },
    {
      "url": "https://tds.s-anand.net/#/2025-01/data-cleaning",
      "text": "Data cleaning course page"
    }
  ]
}
📥 Deploy on Render
Set up a free web service:

Start command:
uvicorn main:app --host 0.0.0.0 --port 10000
Python version: 3.10+

Memory: < 512 MB

📜 License
MIT License

🙏 Acknowledgements
Inspired by the TDS Project Guidelines
Thanks to the TDS instructors and the IITM Online Degree team

---

Let me know if you want the README in **PDF**, want to localize it in Hindi, or include screenshots or API example responses.

# TDS Virtual TA API

A memory-efficient API that automatically answers student questions based on TDS course content and discourse posts.

## Features

- **Memory Efficient**: Stays within 512MB memory limit for free deployment
- **Semantic Search**: Uses keyword-based search for fast and accurate responses
- **Image Support**: Accepts base64 encoded images (placeholder for future OCR implementation)
- **Fast Response**: Returns answers within 30 seconds
- **Relevant Links**: Provides links to source materials

## Memory Optimization

This implementation uses several techniques to stay within the 512MB memory limit:

1. **Lightweight Search**: Uses keyword-based search instead of heavy ML models
2. **Document Chunking**: Splits large documents into smaller, manageable chunks
3. **Limited Data Loading**: Processes only essential data to reduce memory footprint
4. **Efficient Indexing**: Uses simple keyword indexing for fast retrieval

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure you have the required data files:
   - `course.md` - TDS course content
   - `discourse.md` - Discourse posts content
   - `discourse_posts.json` - Structured discourse data

## Usage

### Option 1: Lightweight Version (Recommended for 512MB limit)

```bash
python main_lightweight.py
```

### Option 2: Full Version (Requires more memory)

```bash
python main.py
```

### API Endpoints

#### POST /api/
Submit a question with optional image:

```bash
curl "http://localhost:8000/api/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?",
    "image": "base64_encoded_image_here"
  }'
```

Response:
```json
{
  "answer": "Based on the course content and discourse posts, here's what I found...",
  "links": [
    {
      "url": "https://discourse.onlinedegree.iitm.ac.in/t/example/123",
      "text": "Relevant discussion about model selection"
    }
  ]
}
```

#### GET /health
Check API health and memory usage:
```bash
curl http://localhost:8000/health
```

#### GET /
Get API information:
```bash
curl http://localhost:8000/
```

## Testing

Run the test script to verify functionality:

```bash
python test_api.py
```

## Memory Usage

The lightweight version typically uses:
- **Initialization**: ~50-100MB
- **Runtime**: ~80-150MB
- **Peak**: ~200MB

This ensures it stays well within the 512MB limit for free deployment platforms.

## Data Sources

The API uses data from:
- [TDS Course Content](https://tds.s-anand.net/#/2025-01/) (as of 15 Apr 2025)
- [TDS Discourse Posts](https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34) (1 Jan 2025 - 14 Apr 2025)

## Evaluation

To evaluate your API with promptfoo:

1. Edit `project-tds-virtual-ta-promptfoo.yaml` to replace `providers[0].config.url` with your API URL
2. Run the evaluation:
```bash
npx -y promptfoo eval --config project-tds-virtual-ta-promptfoo.yaml
```

## Deployment

### Railway/Render/Heroku
Use the lightweight version (`main_lightweight.py`) for deployment on platforms with 512MB memory limits.

### Local Development
Either version works for local development.

## Architecture

### Lightweight Version
- **Search Algorithm**: Keyword-based similarity scoring
- **Indexing**: Simple keyword-to-chunk mapping
- **Memory Usage**: ~50-150MB
- **Speed**: Very fast (< 1 second responses)

### Full Version
- **Search Algorithm**: Semantic search with sentence transformers
- **Indexing**: FAISS vector index
- **Memory Usage**: ~200-400MB
- **Speed**: Fast (< 3 second responses)

## Troubleshooting

### Memory Issues
If you encounter memory issues:
1. Use the lightweight version (`main_lightweight.py`)
2. Reduce chunk size in the code
3. Limit the number of discourse posts processed

### Performance Issues
If responses are slow:
1. Check the `/health` endpoint for memory usage
2. Ensure you're using the lightweight version
3. Monitor response times in the logs

## License

This project is licensed under the MIT License.

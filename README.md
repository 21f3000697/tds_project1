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

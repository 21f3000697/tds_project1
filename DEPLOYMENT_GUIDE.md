# TDS Virtual TA API - Deployment Guide

## Quick Start

### For 512MB Memory Limit (Recommended)

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Start the lightweight version:**
```bash
python main_lightweight.py
```

3. **Test the API:**
```bash
python test_api.py
```

## Memory-Efficient Implementation

### Key Features
- ✅ **Memory Usage**: ~50-150MB (well under 512MB limit)
- ✅ **Response Time**: < 30 seconds
- ✅ **Image Support**: Accepts base64 images
- ✅ **Semantic Search**: Keyword-based similarity matching
- ✅ **Relevant Links**: Extracts source links from content

### Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │───▶│  Lightweight TA  │───▶│  Document Store │
│   (main_light)  │    │  (utils_light)   │    │  (course.md)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   HTTP Response │    │ Keyword Index    │    │  discourse.md   │
│   (JSON)        │    │ (Fast Search)    │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## API Endpoints

### POST /api/
**Purpose**: Answer student questions

**Request:**
```json
{
  "question": "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?",
  "image": "base64_encoded_image_optional"
}
```

**Response:**
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

### GET /health
**Purpose**: Check API health and memory usage

**Response:**
```json
{
  "status": "healthy",
  "message": "TDS Virtual TA is running",
  "memory_usage_mb": 85.2,
  "memory_limit_mb": 512
}
```

## Deployment Options

### 1. Railway (Recommended)
```bash
# Deploy to Railway
railway login
railway init
railway up
```

**Railway Configuration:**
- Use `main_lightweight.py` as entry point
- Set environment variables if needed
- Memory limit: 512MB (free tier)

### 2. Render
```bash
# Create render.yaml
services:
  - type: web
    name: tds-virtual-ta
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main_lightweight.py
```

### 3. Heroku
```bash
# Use Procfile (already created)
web: python main_lightweight.py

# Deploy
heroku create your-app-name
git push heroku main
```

### 4. Local Development
```bash
# Start with automatic version selection
python start.py

# Or manually choose version
python main_lightweight.py  # Lightweight (recommended)
python main.py             # Full version (more memory)
```

## Memory Optimization Techniques

### 1. Document Chunking
- Splits large documents into 300-character chunks
- Reduces memory footprint while maintaining context

### 2. Keyword Indexing
- Creates fast keyword-to-chunk mapping
- Avoids loading heavy ML models

### 3. Limited Data Processing
- Processes only first 500 discourse posts
- Filters out unnecessary content

### 4. Efficient Search
- Uses TF-IDF-like similarity scoring
- Fast retrieval without vector embeddings

## Testing

### Automated Tests
```bash
python test_api.py
```

### Manual Testing
```bash
# Test question endpoint
curl -X POST "http://localhost:8000/api/" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is PromptFoo?"}'

# Test health endpoint
curl "http://localhost:8000/health"
```

### Memory Monitoring
```bash
# Check memory usage
curl "http://localhost:8000/health" | jq '.memory_usage_mb'
```

## Troubleshooting

### Memory Issues
**Problem**: App exceeds 512MB memory limit
**Solution**: 
1. Use `main_lightweight.py` instead of `main.py`
2. Reduce chunk size in `utils_lightweight.py`
3. Limit discourse posts processed

### Performance Issues
**Problem**: Slow response times
**Solution**:
1. Check memory usage with `/health` endpoint
2. Ensure using lightweight version
3. Monitor logs for bottlenecks

### Import Errors
**Problem**: Missing dependencies
**Solution**:
```bash
pip install -r requirements.txt
```

## Evaluation with PromptFoo

1. **Get your API URL** (e.g., `https://your-app.railway.app`)

2. **Edit evaluation config:**
```yaml
# project-tds-virtual-ta-promptfoo.yaml
providers:
  - id: your-api
    config:
      url: https://your-app.railway.app/api/
      method: POST
      headers:
        Content-Type: application/json
```

3. **Run evaluation:**
```bash
npx -y promptfoo eval --config project-tds-virtual-ta-promptfoo.yaml
```

## Data Sources

The API uses data from:
- **Course Content**: [TDS Course](https://tds.s-anand.net/#/2025-01/) (as of 15 Apr 2025)
- **Discourse Posts**: [TDS Discourse](https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34) (1 Jan 2025 - 14 Apr 2025)

## File Structure

```
TDS_project1/
├── main_lightweight.py      # Lightweight API server
├── utils_lightweight.py     # Memory-efficient TA implementation
├── main.py                  # Full version (more memory)
├── utils.py                 # Full version implementation
├── test_api.py             # Test script
├── start.py                # Auto-startup script
├── requirements.txt        # Dependencies
├── Procfile               # Heroku deployment
├── course.md              # Course content
├── discourse.md           # Discourse content
├── discourse_posts.json   # Structured discourse data
└── README.md              # Project documentation
```

## Performance Metrics

### Lightweight Version
- **Memory Usage**: 50-150MB
- **Response Time**: < 1 second
- **Accuracy**: Good for keyword-based queries
- **Scalability**: Excellent for 512MB environments

### Full Version
- **Memory Usage**: 200-400MB
- **Response Time**: < 3 seconds
- **Accuracy**: Better semantic understanding
- **Scalability**: Requires more memory

## Support

For issues or questions:
1. Check the `/health` endpoint for system status
2. Review logs for error messages
3. Test with simple questions first
4. Ensure all data files are present

## License

This project is licensed under the MIT License. 
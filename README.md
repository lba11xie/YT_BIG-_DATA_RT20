# YouTube Big Data Analytics Project

A complete **end-to-end Big Data pipeline** that collects YouTube trending data, processes it with Apache Spark, and visualizes insights in a premium Streamlit dashboard.

##  Project Structure
```
c:\JELLYFISH\YT_BD\YT_BD\
├── config.py               ← API Key, DB credentials, paths
├── requirements.txt
├── run_pipeline.py         ← ONE-CLICK full pipeline runner
│
├── collector\              ← YouTube API data fetching
│   ├── youtube_collector.py
│   ├── comment_collector.py
│   └── run_collection.py
│
├── db\                     ← MySQL database layer
│   ├── setup_db.py
│   ├── db_connector.py
│   └── insert_data.py
│
├── spark\                  ← Apache Spark processing
│   ├── spark_processor.py
│   ├── sentiment_analysis.py
│   └── export_results.py
│
├── dashboard\              ← Streamlit dashboard
│   ├── app.py
│   └── pages\
│       ├── 1_Overview.py
│       ├── 2_Category_Analysis.py
│       ├── 3_Sentiment.py
│       └── 4_WordCloud.py
│
└── data\
    ├── raw\                ← videos.json, comments.json, .csv files
    └── processed\          ← Spark output files
```

## Tech Stack
| Layer | Tool |
|-------|------|
| API | YouTube Data API v3 |
| Language | Python 3.11 |
| Processing | Apache Spark (PySpark) |
| Storage | MySQL 8.x |
| NLP | TextBlob Sentiment |
| Visualization | Streamlit + Plotly + WordCloud |

##  Quick Start (One Command!)
```bash
python c:\JELLYFISH\YT_BD\YT_BD\run_pipeline.py
```
This runs all 5 stages automatically:
1. Creates MySQL database & tables
2. Fetches 200 trending YouTube videos (India region)
3. Fetches top 20 comments per video
4. Runs PySpark processing + sentiment analysis
5. Launches Streamlit dashboard at http://localhost:8501

##  Install Dependencies
```bash
python -m pip install -r requirements.txt
```

##  MySQL Configuration
Default: `host=localhost, user=root, password=root, db=yt_bigdata`

To change, edit `config.py`:
```python
DB_USER     = "root"
DB_PASSWORD = "your_password"
```

##  Dashboard Pages
| Page | Description |
|------|-------------|
| Home | Stats overview + pipeline diagram |
| Top Videos | Bar charts, scatter, video cards |
|  Categories | Pie, bar, bubble charts by category |
|  Sentiment | Donut chart, comment sentiment viewer |
|  Word Cloud | Interactive word cloud + frequency bars |

##  Run Individual Steps
```bash
# Step 1: Setup DB only
python c:\JELLYFISH\YT_BD\YT_BD\db\setup_db.py

# Step 2: Collect data only
python c:\JELLYFISH\YT_BD\YT_BD\collector\run_collection.py

# Step 3: Insert to MySQL
python c:\JELLYFISH\YT_BD\YT_BD\db\insert_data.py

# Step 4: Run Spark
python c:\JELLYFISH\YT_BD\YT_BD\spark\export_results.py

# Step 5: Launch dashboard
streamlit run c:\JELLYFISH\YT_BD\YT_BD\dashboard\app.py
```



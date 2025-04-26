# Vinted Average Price API

Simple Flask API that fetches live Vinted listings and calculates the average sell price.

## How to Run

- Clone repo
- Install requirements: `pip install -r requirements.txt`
- Run locally: `python app.py`

## Deploying

- Connect GitHub repo to Render.com
- Add Build Command: `pip install -r requirements.txt`
- Add Start Command: `gunicorn app:app`
- Deploy 🚀
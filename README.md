<img width="1919" height="945" alt="image" src="https://github.com/user-attachments/assets/843271ed-2279-4c2e-8ed7-e4cafae330e8" />
<img width="1919" height="961" alt="image" src="https://github.com/user-attachments/assets/f329861b-bd2f-46d4-9418-21016178ad58" />
<img width="1919" height="953" alt="image" src="https://github.com/user-attachments/assets/3261e7ca-8c18-4ef1-a785-9ef364941137" />



🚀 SmartInsight — Understanding APIs Through a Real Product

SmartInsight is a Django-based web application built to demonstrate how APIs work in real-world applications.

Instead of just explaining APIs theoretically, this project integrates multiple external APIs into one intelligent dashboard that combines:

🌤 Weather data

🔮 Horoscope insights

💬 Motivational quotes

📈 Forecast trends

🖼 Dynamic image content

📚 Author background data

This project was built to deeply understand:

How APIs communicate over HTTP

Authentication via API keys

JSON parsing

Error handling

Rate limits

Caching strategies

Combining multiple APIs into one coherent system

🧠 What This Project Demonstrates
1️⃣ How APIs Work (Practical Understanding)

This project consumes multiple external APIs:

API	Purpose
API Ninjas	Weather + Horoscope + Quotes
Open-Meteo	7-Day Forecast
Pexels	Dynamic Images
Wikipedia	Author Summaries

It demonstrates:

Sending HTTP requests with headers

Passing query parameters

Parsing JSON responses

Handling failed responses

Managing API rate limits

Structuring reusable service layers

🏗 Architecture Overview

The project follows a clean separation of concerns:

dashboard/
│
├── views.py              # Controller logic
├── services/             # External API integrations
│   ├── apininjas.py
│   ├── openmeteo.py
│   ├── wiki.py
│   └── pexels.py
├── models.py             # Search history tracking
├── templates/
└── static/
🔹 Services Layer

All external APIs are isolated inside services/.
This keeps views clean and improves maintainability.

🔹 Caching Strategy

To avoid hitting API rate limits:

Weather → cached for 10 minutes

Horoscope → cached for 6 hours

Quote → cached for 1 hour

Images → cached for 6 hours

Django’s cache framework is used.

🎯 Key Features
🌤 Weather Dashboard

Live temperature

Humidity

Cloud percentage

Wind speed

Smart weather mode detection (sunny / rainy / cloudy / mild)

7-day forecast visualization using Chart.js

Dynamic weather-based UI animation

🔮 Horoscope Insights

Daily horoscope reading

Zodiac traits integration

Element-based personality mapping

Dynamic image gallery

Smart daily brief generation

💬 Quotes Module

Random quote generator

Save to favorites

Quote history tracking

Author biography via Wikipedia API

Author image search via Pexels API

🔐 API Authentication

APIs requiring authentication use header-based API keys:

headers = {
    "X-Api-Key": YOUR_API_KEY
}

The project demonstrates:

Securing keys

Handling expired keys

Handling rate limits

Graceful error messages

📊 Smart Daily Insight Engine

The dashboard includes a rule-based logic system that merges:

Zodiac element

Current weather conditions

Humidity

Temperature

To generate a contextual daily brief like:

“Push forward with bold decisions. Conditions are balanced today.”

This demonstrates how raw API data can be transformed into meaningful application logic.

🧩 Core Concepts Learned

This project was built to deeply understand:

REST APIs

HTTP request lifecycle

JSON data structures

Django view flow

Service abstraction

Caching strategies

Rate limiting issues

Defensive error handling

Combining multiple APIs into one product

🛠 Tech Stack

Python

Django

Bootstrap 5

Chart.js

External REST APIs

Django Cache Framework


📌 Why This Project Matters

Many tutorials teach APIs in isolation.

This project demonstrates:

How APIs power real applications.

It shows how to:

Combine multiple APIs

Design for failure

Manage rate limits

Create intelligent UI responses

Build something that feels like a product

👨‍💻 Author

Built by Erick (DevLoom)
Backend Engineer | Django | API Integration | System Design

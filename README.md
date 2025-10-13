# Real-Time AI Stock Prediction Platform

![Platform Banner](https://i.imgur.com/your-banner-image-url.png) <!-- Optional: Create and add a banner image -->

A full-stack, real-time stock analysis and prediction platform built with a sophisticated backend featuring Vue.js, Flask, Apache Kafka for messaging, and Apache Spark (MLlib) for machine learning.

This application provides a "Trading Terminal" style interface for viewing continuous stock price updates and live AI-powered price predictions.

---

## ✨ Key Features

-   **Real-Time Price & Graph Updates**: The stock detail page provides a fluid, continuous visualization of the day's stock performance. The graph doesn't refresh; it extends in real-time as new data arrives via a Kafka-powered stream.
-   **Live AI Price Prediction (Next 5 Mins)**: When viewing a stock during market hours, a live MLlib model predicts the price for the next 5-minute interval. This prediction is re-calculated and updated continuously based on the latest price data.
-   **Next-Day Outlook Prediction**: For closed markets (weekends/after-hours), a separate classification model predicts the likely direction (Increase 📈 or Decrease 📉) for the next trading day.
-   **On-Demand "Just-in-Time" Model Training**: The system is fully autonomous. When a user views a stock for which a prediction model doesn't exist, a Kafka message is sent to a dedicated training service that automatically builds, trains, and deploys the model in the background without any user intervention or downtime.
-   **Fully Interactive Financial Charts**:
    -   **Fixed Timeline**: Charts always display the full trading day (9:15 AM - 3:30 PM), with live data filling in the timeline.
    -   **Interactive Tooltip & Crosshair**: Hovering over the chart reveals a vertical line pointer and a detailed tooltip showing the price at any point in time.
    -   **Previous Close Baseline**: A dashed horizontal line provides instant visual context of the current price relative to the previous day's close.
    -   **Glowing Edge Effect**: A beautiful "glowing line" effect on top of a shaded area chart, which is perfectly aligned and visually polished.
-   **Dynamic Favorites/Watchlist**: Users can add and remove stocks from a persistent favorites list on the dashboard. Adding a favorite automatically triggers on-demand model training and prediction for that stock.
-   **Modern "Trading Terminal" UI/UX**:
    -   A full-screen, data-rich interface that mimics professional trading applications.
    -   A beautiful, non-distracting animated "starfield" background.
    -   An "Inspector" style sidebar for detailed data analysis.
    -   Polished typography with monospaced fonts for numerical data.
-   **Decoupled & Scalable Backend Architecture**: The system uses a message-driven architecture with Apache Kafka as the central message bus, decoupling the web server from the heavy data processing and machine learning tasks.

---

## 📸 Screenshots

*A picture is worth a thousand words. Replace these placeholders with your own screenshots.*

**Main Dashboard**
*(Displays favorite stocks with real-time price updates)*
<!-- Add your StockDashboard.vue screenshot here -->
`![Dashboard Screenshot](path/to/your/dashboard_screenshot.png)`

**Stock Detail Terminal**
*(The main "Trading Terminal" UI with the interactive chart, live price, and AI prediction)*
<!-- Add your StockDetail.vue screenshot here -->
`![Detail Page Screenshot](path/to/your/detail_page_screenshot.png)`

---

## 🛠️ Technology Stack

-   **Frontend**: Vue 3 (Composition API), Vite, Axios, Chart.js
-   **Backend Web Server**: Flask
-   **Data Streaming / Messaging**: Apache Kafka, `confluent-kafka` (Python client)
-   **Machine Learning / Data Processing**: Apache Spark (MLlib & PySpark)
-   **Data Storage**:
    -   **Favorites/Cache**: Local JSON files
    -   **Models**: Saved Spark ML models on the local filesystem

---

## 🚀 Getting Started

Follow these instructions to get the project running on your local machine.

### Prerequisites

-   **Python 3.9**: This project is built and stabilized on Python 3.9.
-   **Conda**: For managing the Python environment.
-   **Node.js and npm**: For running the Vue.js frontend.
-   **Apache Kafka & Zookeeper**: Must be installed and running. Using Docker is the recommended approach.
-   **Apache Spark**: A local installation is required to use `spark-submit`.

### Setup Instructions

**1. Clone the Repository**
```bash
git clone <your-repository-url>
cd Stock_prediction

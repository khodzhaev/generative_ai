# 📊 Lecture 05: Chat with PDF and Code Interpreter with CSV

This project contains two parts showcasing the use of OpenAI's **code interpreter** and **chat with documents** features.

---

## 🧾 PART 1: Chat with a 100+ page PDF

### 🔗 Data Source
[Sample PDF (uploaded)](./chat-with-data.pdf)

### 💬 Prompt used:
```
Summarize the document structure and key concepts in 10 bullet points.
```

### 🖼️ Screenshot:
![Chat with PDF](screenshots/chat_with_pdf_result.png)

---

## 📈 PART 2: Code Interpreter with a CSV (1,000+ rows)

### 🔗 Data Source
[Sample CSV: Airbnb NYC Listings (Kaggle)](https://www.kaggle.com/datasets/dgomonov/new-york-city-airbnb-open-data)

### 💬 Prompt used:
```
Using the dataset, build a histogram showing distribution of prices. Use matplotlib and include axis labels.
```

### 🖼️ Screenshot:
![Histogram from CSV](screenshots/histogram_result.png)

---

## 💡 Summary

- Used OpenAI ChatGPT Pro with Code Interpreter enabled
- PDF processed using native "Chat with PDF" capability
- CSV analyzed using Python (Pandas + Matplotlib)

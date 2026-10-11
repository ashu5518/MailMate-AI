# 🤖 AI Email Reply Generator using NLP

An AI-powered Email Reply Generator that uses Natural Language Processing (NLP) to analyze incoming emails and generate appropriate replies automatically.

The system analyzes the email's **sentiment, intent, and keywords**, and then uses an AI language model to generate a suitable response based on the selected tone.

---

## 📌 Project Overview

Replying to emails manually can be time-consuming, especially when a user receives many emails every day.

This project provides an intelligent solution that:

- Accepts an email as input
- Cleans and preprocesses the email
- Detects the email sentiment
- Identifies the user's intent
- Extracts important keywords
- Generates an AI-based reply
- Allows the user to select the reply tone
- Allows the generated reply to be copied

---

## 🎯 Objectives

The main objectives of this project are:

1. To automate email reply generation.
2. To use NLP for understanding email content.
3. To detect the sentiment of incoming emails.
4. To identify the intent of an email.
5. To generate context-aware email responses.
6. To provide different reply tones.
7. To create a simple and user-friendly web application.

---

## 🚀 Features

### 1. Email Input

Users can paste or type an email into the input box.

### 2. Sentiment Analysis

The application identifies the sentiment of the email:

- Positive
- Negative
- Neutral

### 3. Intent Detection

The application can detect intents such as:

- Meeting / Appointment
- Payment / Invoice
- Leave Request
- Problem / Complaint
- Thank You
- Information Request
- Job / Career
- Order / Delivery
- General

### 4. Keyword Extraction

Important words from the email are extracted using NLP-based text processing.

### 5. AI Reply Generation

The system generates an appropriate reply according to the email context.

### 6. Tone Selection

Users can select the desired tone:

- Professional
- Formal
- Friendly
- Short and Concise
- Polite

### 7. Copy Reply

The generated reply can be copied to the clipboard.

---

## 🛠️ Technologies Used

### Frontend

- HTML5
- CSS3
- JavaScript

### Backend

- Python
- Flask

### NLP

- Hugging Face Transformers
- DistilBERT
- Regular Expressions

### AI

- Ollama
- Llama 3.2

---

## 📂 Project Structure

```text
AI_Email_Reply_Generator/
│
├── app.py
├── nlp_processor.py
├── requirements.txt
├── README.md
│
├── templates/
│   └── index.html
│
└── static/
    ├── style.css
    └── script.js
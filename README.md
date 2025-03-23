# News Summarization and Text-to-Speech Application

This project is a web-based application that extracts news articles for a given company, performs sentiment analysis, conducts comparative analysis, and generates Hindi audio summaries. It is built using Streamlit and deployed on Hugging Face Spaces.

## Objective
Develop a tool that:
- Extracts news articles related to a user-specified company.
- Performs sentiment analysis (positive, negative, neutral) on each article.
- Conducts a comparative sentiment analysis across articles.
- Generates Hindi audio summaries using text-to-speech (TTS).
- Provides a simple web interface for user interaction.

## Requirements
- **News Extraction**: Scrapes articles using `BeautifulSoup` from `.edu`, `.org`, and `.gov` domains.
- **Sentiment Analysis**: Uses NLTK's VADER model to classify sentiment.
- **Comparative Analysis**: Compares sentiment across articles and provides a summary.
- **Text-to-Speech**: Converts summaries to Hindi audio using `gTTS` with translation via `deep-translator`.
- **User Interface**: Built with Streamlit, allowing users to input a company name.
- **API Development**: Backend functions are called via APIs defined in `api.py`.
- **Deployment**: Hosted on Hugging Face Spaces.
- **Documentation**: This README provides setup and usage instructions.

## Project Structure
- `app.py`: Main Streamlit application.
- `utils.py`: Utility functions for scraping, summarization, and TTS.
- `models.py`: Sentiment analysis using NLTK VADER.
- `api.py`: API for communication between frontend and backend.
- `requirements.txt`: List of dependencies.

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Zoro9999999/news-summarizer.git
   cd news-summarizer
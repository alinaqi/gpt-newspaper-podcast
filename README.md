# GPT Newspaper

> This is a fork of [rotemweiss57/gpt-newspaper](https://github.com/rotemweiss57/gpt-newspaper) with significant improvements:
> - Integrated Perplexity AI for more accurate and up-to-date news search
> - Upgraded to use latest GPT models (GPT-4 Turbo) for better content generation
> - Enhanced error handling and logging throughout the application
> - Improved JSON response validation and processing
> - Better date handling in article curation

Welcome to the GPT Newspaper project, an innovative autonomous agent designed to create personalized newspapers tailored to user preferences. GPT Newspaper revolutionizes the way we consume news by leveraging the power of AI to curate, write, design, and edit content based on individual tastes and interests.

## 🔍 Overview

GPT Newspaper consists of six specialized sub-agents in LangChain's new [LangGraph Library](https://github.com/langchain-ai/langgraph):

1. **Search Agent**: Scours the web for the latest and most relevant news using Perplexity AI's powerful search capabilities.
2. **Curator Agent**: Filters and selects news based on user-defined preferences and interests.
3. **Writer Agent**: Crafts engaging and reader-friendly articles.
4. **Critique Agent** Provide feedback to the writer until article is approved.
5. **Designer Agent**: Layouts and designs the articles for an aesthetically pleasing reading experience.
6. **Editor Agent**: Constructs the newspaper based on produced articles.
7. **Publisher Agent** Publishes the newspaper to the frontend or desired service

Each agent plays a critical role in delivering a unique and personalized newspaper experience.

<div align="center">
<img align="center" height="500" src="https://tavily-media.s3.amazonaws.com/gpt-newspaper-architecture.png">
</div>


## Demo
https://github.com/assafelovic/gpt-newspaper/assets/91344214/7f265369-1293-4d95-9be5-02070f12c67e


## 🌟 Features

- **Personalized Content**: Get news that aligns with your interests and preferences.
- **Advanced Search**: Utilizes Perplexity AI's state-of-the-art search capabilities for comprehensive and up-to-date news gathering.
- **Diverse Sources**: Aggregates content from a wide range of reputable news sources, including recent social media discussions.
- **Engaging Design**: Enjoy a visually appealing layout and design.
- **Quality Assurance**: Rigorous editing ensures reliable and accurate news reporting.
- **User-Friendly Interface**: Easy-to-use platform for setting preferences and receiving your newspaper.

## 🛠️ How It Works

1. **Setting Preferences**: Users input their interests, preferred topics, and news sources.
2. **Automated Curation**: The Search Agent uses Perplexity AI to find the latest news, while the Curator Agent selects the most relevant stories.
3. **Content Creation**: The Writer Agent drafts articles, which are then designed by the Designer Agent.
4. **Newspaper Design**: The Editor Agent reviews and finalizes the content.
5. **Delivery**: Users receive their personalized newspaper to their mailbox.

## 🚀 Getting Started

### Prerequisites

- Perplexity API Key - [Sign Up](https://www.perplexity.ai/)
- OpenAI API Key - [Sign Up](https://platform.openai.com/)
- Tavily API Key - [Sign Up](https://tavily.com/)

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/rotemweiss57/gpt-newspaper.git
    ```
2. Export your API Keys
   ```sh
    export PERPLEXITY_API_KEY=<YOUR_PERPLEXITY_API_KEY>
    export OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
    export TAVILY_API_KEY=<YOUR_TAVILY_API_KEY>
    ```
3. Install Requirements
   ```sh
   pip install -r requirements.txt
   ```
4. Run the app
   ```sh
    python app.py
    ```
5. Open the app in your browser
   ```sh
    http://localhost:5000/
    ```
6. Enjoy!

## 🤝 Contributing

Interested in contributing to GPT Newspaper? We welcome contributions of all kinds! Check out our [Contributor's Guide](CONTRIBUTING.md) to get started.


## 🛡️ Disclaimer

GPT Newspaper is an experimental project and provided "as-is" without any warranty. It's intended for personal use and not as a replacement for professional news outlets.

## 📩 Contact Us

For support or inquiries, please reach out to us:

- [Email](mailto:ashaheen@workhub.ai)

Join us in redefining the future of news consumption with GPT Newspaper!

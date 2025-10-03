# AdPoster - Social Media Ad Generator

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.2-lightgrey.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

AdPoster is a comprehensive web application that automatically generates and posts promotional content for Android apps across multiple social media platforms using AI-powered content generation.

## ✨ Features

- **AI-Powered Content Generation**: Uses Google Gemini AI to create engaging ad copy tailored for each platform
- **Multi-Platform Support**: Generate and post to Facebook, Twitter, Instagram, Bluesky, LinkedIn, TikTok, and Reddit
- **Image Generation**: Automatically creates custom images for your ads using AI
- **Web Interface**: User-friendly dashboard for managing campaigns and viewing results
- **Campaign Management**: Create, view, and delete ad campaigns with full tracking
- **Platform-Specific Optimization**: Content is automatically optimized for each social media platform's requirements
- **Configuration Management**: Easy-to-use web interface for managing API keys and settings

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git
- API keys for desired social media platforms

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/epicquest/AdPoster.git
   cd AdPoster
   ```

2. **Create and activate virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API keys:**
   - Copy the default configuration: `cp configuration/default_config.json configuration/config.json`
   - Edit `configuration/config.json` and add your API keys:
     - Google Gemini API key (required for AI content generation)
     - Social media platform API keys (optional, only needed for platforms you want to post to)

5. **Start the application:**

   ```bash
   ./start-server.sh
   ```

6. **Open your browser:**
   - Navigate to `http://127.0.0.1:5000`
   - Access the web interface to start generating ads!

## 📋 Configuration

### Required API Keys

#### Google Gemini AI (Required)

- Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- Add it to `configuration/config.json` under `google_api_key`

#### Optional Platform APIs

**Facebook:**
- Page ID and Access Token from [Facebook Developers](https://developers.facebook.com/)

**Instagram:**
- App ID, Account ID, and Access Token from [Facebook Developers](https://developers.facebook.com/)

**Twitter/X:**
- API Key, API Secret, Bearer Token, Access Token, and Access Token Secret from [Twitter Developer Portal](https://developer.twitter.com/)

**Bluesky:**
- Handle and App Password from your Bluesky account settings

**LinkedIn:**
- API credentials from [LinkedIn Developers](https://developer.linkedin.com/)

**TikTok:**
- API credentials from [TikTok Developers](https://developers.tiktok.com/)

**Reddit:**
- Client ID and Client Secret from [Reddit Apps](https://www.reddit.com/prefs/apps/)

### Image Hosting Services

**ImgBB:**
- API key from [ImgBB](https://imgbb.com/) for free image hosting

**ImageKit:**
- Public/Private keys and URL endpoint from [ImageKit](https://imagekit.io/)

## 🎯 Usage

### 1. Configure Your App Templates

1. Go to the "Manage Apps" section in the web interface
2. Add your Android app details:
   - App name and description
   - Category and key features
   - Target audience
   - App URL (Google Play Store, App Store, or direct download link)

### 2. Generate Ad Campaigns

1. Click "Generate New Ad" from the dashboard
2. Select your app from the dropdown
3. Choose which platforms to generate content for
4. Click "Generate Ads"

The system will:

- Create platform-specific ad copy using AI
- Generate custom images for each platform
- Display the results in your campaign dashboard

### 3. Review and Post

1. View generated campaigns in the dashboard
2. Click on any campaign to see detailed content for each platform
3. Use the posting functionality to automatically publish to your configured platforms
4. Track posting status and results

### 4. Manage Campaigns

- View all your campaigns on the main dashboard
- Delete unwanted campaigns using the delete button
- Monitor posting status across all platforms

## 🏗️ Project Structure

```
AdPoster/
├── app/                          # Main application code
│   ├── templates/               # Jinja2 HTML templates
│   ├── static/                  # CSS, JS, images
│   ├── config.py                # Configuration management
│   ├── web_interface.py         # Flask web application
│   ├── PosterGenerator.py       # AI content generation
│   ├── AdPoster.py             # Social media posting logic
│   └── [platform]_api/         # Platform-specific API integrations
├── configuration/               # Configuration files
│   ├── config.json             # Your API keys and settings
│   └── default_config.json     # Default configuration template
├── output/                      # Generated campaigns and images
├── requirements.txt             # Python dependencies
├── start-server.sh             # Startup script
└── README.md                   # This file
```

## 🔧 Development

### Setting up Development Environment

1. Follow the installation steps above
2. Install additional development dependencies:

   ```bash
   pip install pytest black flake8
   ```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black app/
```

### Logging

The application logs to both console and files:

- `adposter.log` - General application logs
- `poster_generator.log` - Content generation logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -am 'Add some feature'`
5. Push to the branch: `git push origin feature/your-feature-name`
6. Submit a pull request

## 📝 API Reference

### Web Interface Routes

- `GET /` - Main dashboard
- `GET /generate` - Ad generation form
- `POST /generate` - Generate new ad campaign
- `GET /ad/<filename>` - View specific campaign details
- `POST /campaign/<filename>/delete` - Delete campaign
- `GET /list-apps` - Manage app templates
- `GET /config` - Configuration management

### Configuration Schema

The `config.json` file supports the following keys:

```json
{
  "google_api_key": "your-gemini-api-key",
  "ai_model": "gemini-2.0-flash-lite",
  "fb_page_id": "your-facebook-page-id",
  "fb_access_token": "your-facebook-access-token",
  "twitter_api_key": "your-twitter-api-key",
  "twitter_api_key_secret": "your-twitter-api-secret",
  "twitter_bearer_token": "your-twitter-bearer-token",
  "twitter_access_token": "your-twitter-access-token",
  "twitter_access_token_secret": "your-twitter-access-token-secret",
  "bsky_handle": "your-bluesky-handle",
  "bsky_password": "your-bluesky-password",
  "instagram_app_id": "your-instagram-app-id",
  "instagram_account_id": "your-instagram-account-id",
  "instagram_access_token": "your-instagram-access-token",
  "imgbb_api_key": "your-imgbb-api-key",
  "imagekit_public_key": "your-imagekit-public-key",
  "imagekit_private_key": "your-imagekit-private-key",
  "imagekit_url_endpoint": "your-imagekit-endpoint"
}
```

## 🐛 Troubleshooting

### Common Issues

**"Module not found" errors:**

- Ensure you've activated the virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**API key errors:**

- Verify your API keys are correctly entered in `configuration/config.json`
- Check that API keys haven't expired
- Ensure proper permissions are granted for social media APIs

**Image generation fails:**

- Verify your Google Gemini API key is valid
- Check internet connection for image generation requests

**Posting fails:**

- Confirm platform API credentials are correct
- Check that you have proper permissions on the target accounts
- Verify rate limits haven't been exceeded

### Getting Help

- Check the logs in `adposter.log` and `poster_generator.log`
- Open an issue on GitHub with detailed error messages
- Include your Python version and operating system

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini AI for content generation
- Flask framework for the web interface
- All the social media platforms and their APIs
- The open-source community for various dependencies

## 🔄 Version History

### v1.0.0

- Initial release with multi-platform support
- AI-powered content generation
- Web interface for campaign management
- Support for Facebook, Twitter, Instagram, Bluesky, LinkedIn, TikTok, Reddit

---

Made with ❤️ for Android app developers and marketers

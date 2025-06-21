# 🚀 VisaT - Visa Consulting Automation System

## 📋 Project Overview

**VisaT** is a zero-cost visa consulting automation system for Thailand visa services. The system integrates WhatsApp, Facebook Messenger, Google Forms, and Calendly to automate lead qualification and appointment booking.

## 🎯 Key Features

- **Multi-Channel Contact:** WhatsApp and Facebook Messenger integration
- **Automated Lead Qualification:** Smart filtering based on nationality and financial criteria
- **Professional Communication:** Automated email and WhatsApp responses
- **Appointment Scheduling:** Seamless Calendly integration for qualified leads
- **Data Management:** Google Sheets integration for lead tracking
- **Zero-Cost Architecture:** Built entirely on free service tiers

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Contact       │    │   Lead          │    │   Qualified     │
│   Channels      │───▶│   Capture       │───▶│   Lead          │
│                 │    │                 │    │   Processing    │
│ • WhatsApp      │    │ • Google Forms  │    │                 │
│ • FB Messenger  │    │ • Data Validation│    │ • Email Send    │
│                 │    │                 │    │ • WhatsApp Send │
└─────────────────┘    └─────────────────┘    │ • Calendly Link │
                                              └─────────────────┘
                                                       │
                                              ┌─────────────────┐
                                              │   Data          │
                                              │   Storage       │
                                              │                 │
                                              │ • Google Sheets │
                                              │ • Lead Tracking │
                                              └─────────────────┘
```

## 🛠️ Technology Stack

- **Backend:** Python Flask (hosted on Railway/Render free tier)
- **Forms:** Google Forms API
- **Storage:** Google Sheets API
- **Email:** Gmail SMTP
- **WhatsApp:** WhatsApp Business API
- **Scheduling:** Calendly API
- **Hosting:** Railway/Render free tier

## 📂 Project Structure

```
VisaT/
├── README.md
├── requirements.txt
├── .env.example
├── app.py                 # Main Flask application
├── config/
│   ├── __init__.py
│   ├── settings.py        # Configuration management
│   └── rules.json         # Business rules configuration
├── src/
│   ├── __init__.py
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── contact_handler.py      # WhatsApp/FB message handling
│   │   └── form_processor.py       # Google Forms processing
│   ├── engines/
│   │   ├── __init__.py
│   │   └── qualification_engine.py # Lead qualification logic
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── gmail_client.py         # Email integration
│   │   ├── whatsapp_client.py      # WhatsApp integration
│   │   ├── sheets_client.py        # Google Sheets integration
│   │   └── calendly_client.py      # Calendly integration
│   └── utils/
│       ├── __init__.py
│       ├── validators.py           # Data validation
│       └── templates.py            # Message templates
├── templates/
│   ├── emails/
│   │   ├── acceptance.html
│   │   └── rejection.html
│   └── messages/
│       ├── whatsapp_templates.py
│       └── facebook_templates.py
├── tests/
│   ├── __init__.py
│   ├── test_qualification.py
│   ├── test_integrations.py
│   └── test_handlers.py
└── docs/
    ├── setup.md
    ├── api_documentation.md
    └── deployment.md
```

## 🚀 Quick Start

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd VisaT
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp env.example .env
   # Edit .env with your API credentials
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

## 🔧 Configuration

### Business Rules Configuration

Edit `config/rules.json` to modify qualification criteria:

```json
{
    "financial_threshold": 500000,
    "currency": "BTH",
    "blocked_nationalities": [
        "Country1", "Country2", "Country3"
    ],
    "special_rules": [
        {
            "name": "thailand_visa_check",
            "condition": "location == 'Thailand'",
            "requirements": ["visa_type_required"]
        }
    ]
}
```

### API Credentials

Required environment variables in `.env`:
- `GOOGLE_SHEETS_CREDENTIALS`
- `GMAIL_SMTP_PASSWORD`
- `WHATSAPP_API_TOKEN`
- `CALENDLY_API_KEY`
- `FACEBOOK_PAGE_ACCESS_TOKEN`

## 📊 User Journey

1. **Initial Contact:** Customer messages WhatsApp/Facebook
2. **Automated Response:** System sends Google Form link
3. **Data Collection:** Customer completes qualification form
4. **Qualification:** System evaluates based on business rules
5. **Communication:** Automated email + WhatsApp response
6. **Scheduling:** Qualified leads receive Calendly link
7. **Data Storage:** All interactions stored in Google Sheets

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

Run specific test categories:
```bash
python -m pytest tests/test_qualification.py
python -m pytest tests/test_integrations.py
```

## 🚀 Deployment

### Railway Deployment
1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on git push

### Render Deployment
1. Connect repository to Render
2. Configure environment variables
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python app.py`

## 📈 Monitoring & Analytics

- **Lead conversion rates:** Track form completion to appointment booking
- **Source analysis:** WhatsApp vs Facebook Messenger performance
- **Response times:** Monitor system performance
- **Error tracking:** Comprehensive logging and error handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For questions and support:
- Create an issue in the GitHub repository
- Check the documentation in the `docs/` folder
- Review the test files for usage examples

## 🔄 Project Status

- ✅ **Planning Phase:** Complete
- ✅ **Creative Phase:** Complete  
- 🔄 **Implementation Phase:** In Progress
- ⏳ **Testing Phase:** Pending
- ⏳ **Deployment Phase:** Pending

---

**Built with ❤️ for streamlined visa consulting automation**

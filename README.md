# BlindStyle Backend Setup Guide

## Initial Setup

1. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # On Windows PowerShell
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

Or install packages individually:
```bash
pip install Pillow
pip install python-dotenv
pip install google-generativeai
pip install numpy
pip install chromadb
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

## Future Updates

If you add new packages to the project, update requirements.txt using:
```bash
pip freeze > requirements.txt
```

## Note
Make sure you have Python 3.13+ installed on your system before proceeding with the setup.
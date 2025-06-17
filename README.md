# AI Keyword Extractor

A web application that extracts primary and secondary keywords from any URL using OpenAI's API. Perfect for SEO analysis and content optimization.


## Features

- Extract one primary keyword and three secondary keywords from any URL
- Clean and modern user interface
- Real-time keyword analysis
- SEO-focused keyword extraction
- Error handling and validation

## Prerequisites

- Python 3.7 or higher
- Node.js 14 or higher
- npm (comes with Node.js)
- OpenAI API key

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd PrimaryKeywordFinder
```

### 2. Backend Setup

1. Create a virtual environment (recommended):
```bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
.\venv\Scripts\activate
```

2. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Frontend Setup

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

## Running the Application

### 1. Start the Backend Server

Open a terminal and run:
```bash
cd backend
python app.py
```
The backend server will start on http://localhost:5000

### 2. Start the Frontend Development Server

Open another terminal and run:
```bash
cd frontend
npm start
```
The frontend will automatically open in your default browser at http://localhost:3000

## Usage

1. Open your browser and go to http://localhost:3000
2. Enter a URL in the input field (e.g., https://example.com)
3. Click "Extract Keywords"
4. Wait for the analysis to complete
5. View the results:
   - Primary keyword
   - Three secondary keywords

## Troubleshooting

1. If you get a CORS error:
   - Make sure both backend and frontend servers are running
   - Check that the backend is running on port 5000
   - Verify that the frontend is making requests to http://localhost:5000

2. If you get an API key error:
   - Verify that your OpenAI API key is correctly set in the .env file
   - Make sure the .env file is in the project root directory

3. If the frontend fails to start:
   - Make sure Node.js is installed correctly
   - Try deleting the node_modules folder and running npm install again

## Security Notes

- Never commit your .env file or expose your OpenAI API key
- Keep your API key secure and don't share it publicly
- The application is designed for local use only

## License

This project is licensed under the MIT License - see the LICENSE file for details. 

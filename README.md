# OneSky
## Overview

OneSky is an amazing internal platform that enables Sky employees to connect with volunteering opportunities and contribute to positive change across communities in the UK.

## Setup/ Running the application

### Database Setup
When first running the application or when there are changes to schema.sql:

```
In MYSQL open and run schema.sql located in backend/database/
```

### Frontend Setup
```
cd frontend
```
When first running the application or when there are changes to package.json/package-lock.json:

```
npm install 
```

If you encounter dependency issues, use:
```
npm install --legacy-peer-deps
```

To start the development server:
```
npm run dev
```

### Backend Setup
```
cd backend/functionality
```
When first running the application or when there are changes to requirements.txt:

```
pip3 install -r requirements.txt
```

Activate the virtual environment:
```
source venv/bin/activate   
```
To start the backend server:
```
python3 app.py
```
## Tests

### Running Python Tests
In backend/functionality and from within the virtual environment

Run the test suite:
```
pytest
```

### Running React Tests
In frontend

Run the test suite:
```
npm test
```

# Quizy — AI-Powered Educational Assistant

Quizy is a web application that helps teachers create quizzes automatically from their course documents.

Teachers can upload a course file, generate questions using artificial intelligence, and share quizzes with students. Students can answer the quizzes and receive immediate feedback.

## Project Objective

The objective of this project is to develop an intelligent educational assistant based on course materials.

The application allows:

* Teachers to upload course documents.
* AI to generate questions based only on the uploaded document.
* Teachers to create multiple-choice and open-ended questions.
* Students to complete quizzes online.
* Students to receive instant feedback and scores.

## Main Features

### Teacher Features

* Teacher authentication
* Upload course documents
* Generate quizzes using AI
* View generated quizzes
* Manage quizzes
* View the number of uploaded documents
* View active students
* View recent quiz activity

### Student Features

* Student authentication
* Access available quizzes
* Answer multiple-choice questions
* Answer open-ended questions
* Receive an immediate score
* Receive AI-generated feedback

## Technologies Used

* Python
* Streamlit
* Large Language Model API
* Retrieval-Augmented Generation, or RAG
* PDF and document processing
* HTML and CSS for interface customization
* Database for storing users, documents, quizzes, and results

## How the AI Works

The application uses a RAG pipeline:

1. The teacher uploads a course document.
2. The document text is extracted.
3. The text is divided into smaller sections.
4. These sections are converted into embeddings.
5. The relevant sections are retrieved when generating questions.
6. The language model generates questions using only the retrieved course content.

This approach helps reduce unrelated or incorrect answers.

## Installation

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd quizy
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

On Windows:

```bash
venv\Scripts\activate
```

On Linux or macOS:

```bash
source venv/bin/activate
```

### 4. Install the required libraries

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project directory and add your API key:

```env
LLM_API_KEY=your_api_key_here
```

Do not publish the `.env` file or your API key on GitHub.

Add `.env` to the `.gitignore` file:

```text
.env
venv/
__pycache__/
```

## Running the Application

Run the Streamlit application using:

```bash
streamlit run app.py
```

If the main file is currently `login.py`, use:

```bash
streamlit run login.py
```

The application will normally open at:

```text
http://localhost:8501
```

## Current Project Status

The project is currently under development.

Completed or planned interfaces include:

* Login and registration page
* Teacher dashboard
* Student dashboard
* Document upload page
* Quiz generation page
* Quiz answering interface
* Results and feedback page

## Future Improvements

* Support additional document formats
* Add quiz difficulty levels
* Generate different question types
* Add student performance statistics
* Add teacher analytics
* Export quizzes as PDF
* Improve answer evaluation
* Add multilingual support

## Security

* API keys must be stored in environment variables.
* Uploaded documents should be validated.
* User passwords should be encrypted.
* Students should only access quizzes assigned to them.
* Generated questions should remain based on the uploaded course content.

## Author

Developed by **Fatma Dridi** as part of an internship project.

## License

This project is intended for educational purposes.

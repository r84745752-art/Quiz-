from flask import Flask, render_template, request, jsonify
import re
import json

app = Flask(__name__)

class QuizConverter:
    def parse_txt_content(self, txt_content):
        try:
            questions = []
            question_blocks = txt_content.split('---')
            
            for block in question_blocks:
                block = block.strip()
                if not block:
                    continue
                    
                lines = [line.strip() for line in block.split('\n') if line.strip()]
                
                if len(lines) >= 7:
                    question = {
                        'id': int(lines[0]),
                        'text': lines[1],
                        'options': lines[2:6],
                        'correct_option': lines[6],
                        'solution': lines[7] if len(lines) > 7 else 'कोई समाधान उपलब्ध नहीं'
                    }
                    questions.append(question)
            
            return questions
        except Exception as e:
            raise Exception(f'TXT पार्स करने में त्रुटि: {str(e)}')

    def generate_html(self, questions, test_name, duration, category):
        total_marks = len(questions)
        
        # Safe JSON serialization with proper escaping
        questions_json = json.dumps(questions, ensure_ascii=False)
        
        html_template = f'''<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{test_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
            line-height: 1.6;
            padding: 10px;
        }}
        
        .container {{
            max-width: 100%;
            margin: 0 auto;
        }}
        
        .welcome-screen {{
            text-align: center;
            background: white;
            border-radius: 15px;
            padding: 30px 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        
        .welcome-title {{
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        
        .quiz-stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 25px 0;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
        }}
        
        .start-btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1rem;
            border-radius: 25px;
            cursor: pointer;
            margin-top: 20px;
        }}
        
        .quiz-interface {{
            display: none;
        }}
        
        .question {{
            background: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .option {{
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            cursor: pointer;
            border: 2px solid #e9ecef;
        }}
        
        .option.selected {{
            background: #667eea;
            color: white;
        }}
        
        .navigation {{
            display: flex;
            justify-content: space-between;
            margin: 20px 0;
        }}
        
        .nav-btn {{
            padding: 12px 25px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
        }}
        
        #prev-btn {{
            background: #6c757d;
            color: white;
        }}
        
        #next-btn {{
            background: #667eea;
            color: white;
        }}
        
        .submit-btn {{
            background: #28a745;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 25px;
            cursor: pointer;
            display: none;
            margin: 20px auto;
        }}
        
        .result-container {{
            display: none;
            background: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .score {{
            font-size: 3rem;
            font-weight: bold;
            color: #667eea;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="welcome-screen" id="welcomeScreen">
            <h1 class="welcome-title">Quiz Test</h1>
            <h2>{test_name}</h2>
            <p>{category}</p>
            <div class="quiz-stats">
                <div class="stat-card">
                    <div class="stat-value">{len(questions)}</div>
                    <div>Questions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{total_marks}</div>
                    <div>Marks</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{duration}</div>
                    <div>Minutes</div>
                </div>
            </div>
            <button class="start-btn" onclick="startQuiz()">
                <i class="fas fa-play"></i> Start Quiz
            </button>
        </div>

        <div class="quiz-interface" id="quizInterface">
            <div class="question" id="questionContainer">
                <!-- Questions will be loaded here -->
            </div>
            
            <div class="navigation">
                <button class="nav-btn" id="prevBtn" onclick="prevQuestion()">
                    <i class="fas fa-chevron-left"></i> Previous
                </button>
                <button class="nav-btn" id="nextBtn" onclick="nextQuestion()">
                    Next <i class="fas fa-chevron-right"></i>
                </button>
            </div>
            
            <button class="submit-btn" id="submitBtn" onclick="submitQuiz()">
                Submit Quiz
            </button>
        </div>

        <div class="result-container" id="resultContainer">
            <h2>Quiz Results</h2>
            <div class="score" id="scoreDisplay">0/{total_marks}</div>
            <div id="resultDetails"></div>
            <button class="start-btn" onclick="restartQuiz()" style="margin-top: 20px;">
                <i class="fas fa-redo"></i> Try Again
            </button>
        </div>
    </div>

    <script>
        const questions = {questions_json};
        let currentQuestion = 0;
        let userAnswers = new Array(questions.length).fill(null);
        let timeLeft = {int(duration) * 60};
        let timer;

        function startQuiz() {{
            document.getElementById('welcomeScreen').style.display = 'none';
            document.getElementById('quizInterface').style.display = 'block';
            showQuestion(currentQuestion);
            startTimer();
        }}

        function startTimer() {{
            timer = setInterval(() => {{
                timeLeft--;
                if (timeLeft <= 0) {{
                    submitQuiz();
                }}
            }}, 1000);
        }}

        function showQuestion(index) {{
            const question = questions[index];
            const questionContainer = document.getElementById('questionContainer');
            
            let optionsHtml = '';
            question.options.forEach((option, i) => {{
                const isSelected = userAnswers[index] === (i + 1).toString();
                optionsHtml += `
                    <div class="option ${isSelected ? 'selected' : ''}" 
                         onclick="selectOption(${i + 1})">
                        ${option}
                    </div>
                `;
            }});
            
            questionContainer.innerHTML = `
                <h3>Question ${index + 1} of {len(questions)}</h3>
                <div style="margin: 15px 0; font-size: 1.1rem;">${question.text}</div>
                <div class="options">${optionsHtml}</div>
            `;
            
            document.getElementById('prevBtn').disabled = index === 0;
            document.getElementById('nextBtn').style.display = index === questions.length - 1 ? 'none' : 'block';
            document.getElementById('submitBtn').style.display = index === questions.length - 1 ? 'block' : 'none';
        }}

        function selectOption(optionIndex) {{
            userAnswers[currentQuestion] = optionIndex.toString();
            showQuestion(currentQuestion);
        }}

        function nextQuestion() {{
            if (currentQuestion < questions.length - 1) {{
                currentQuestion++;
                showQuestion(currentQuestion);
            }}
        }}

        function prevQuestion() {{
            if (currentQuestion > 0) {{
                currentQuestion--;
                showQuestion(currentQuestion);
            }}
        }}

        function submitQuiz() {{
            clearInterval(timer);
            
            let correct = 0;
            let incorrect = 0;
            let skipped = 0;
            
            questions.forEach((q, i) => {{
                if (userAnswers[i] === null) {{
                    skipped++;
                }} else if (userAnswers[i] === q.correct_option) {{
                    correct++;
                }} else {{
                    incorrect++;
                }}
            }});
            
            document.getElementById('scoreDisplay').textContent = `${{correct}}/{len(questions)}`;
            document.getElementById('resultDetails').innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0;">
                    <div style="background: #28a745; color: white; padding: 15px; border-radius: 10px;">
                        <div style="font-size: 1.5rem; font-weight: bold;">${{correct}}</div>
                        <div>Correct</div>
                    </div>
                    <div style="background: #dc3545; color: white; padding: 15px; border-radius: 10px;">
                        <div style="font-size: 1.5rem; font-weight: bold;">${{incorrect}}</div>
                        <div>Incorrect</div>
                    </div>
                    <div style="background: #ffc107; color: black; padding: 15px; border-radius: 10px;">
                        <div style="font-size: 1.5rem; font-weight: bold;">${{skipped}}</div>
                        <div>Skipped</div>
                    </div>
                </div>
            `;
            
            document.getElementById('quizInterface').style.display = 'none';
            document.getElementById('resultContainer').style.display = 'block';
        }}

        function restartQuiz() {{
            currentQuestion = 0;
            userAnswers = new Array(questions.length).fill(null);
            timeLeft = {int(duration) * 60};
            
            document.getElementById('resultContainer').style.display = 'none';
            document.getElementById('welcomeScreen').style.display = 'block';
        }}
    </script>
</body>
</html>'''
        return html_template

converter = QuizConverter()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_quiz():
    try:
        data = request.get_json()
        txt_content = data.get('txtContent', '')
        test_name = data.get('testName', 'My Quiz Test')
        duration = data.get('duration', '60')
        category = data.get('category', 'General Knowledge')

        if not txt_content.strip():
            return jsonify({
                'success': False,
                'error': 'कृपया प्रश्न डालें!'
            })

        questions = converter.parse_txt_content(txt_content)
        
        if not questions:
            return jsonify({
                'success': False,
                'error': 'कोई वैध प्रश्न नहीं मिले! कृपया फॉर्मेट चेक करें।'
            })

        html_output = converter.generate_html(questions, test_name, duration, category)
        
        return jsonify({
            'success': True,
            'html': html_output,
            'questionsCount': len(questions)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
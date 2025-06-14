import os
from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
# Allow requests from the Render frontend and localhost
CORS(app, resources={r"/api/*": {"origins": [
    "https://wealthsync-frontend.onrender.com",
    "http://localhost:3000"
]}})

# In-memory database for budget history
budget_history = []

@app.route('/api/budget', methods=['POST'])
def calculate_budget():
    data = request.get_json()
    email = data.get('email')
    income = float(data.get('income'))
    expenses = float(data.get('expenses'))
    savings_goal = float(data.get('savings_goal'))

    # Calculate savings
    savings = income - expenses

    # Fetch inflation rate (mocked for simplicity; in production, use a real API)
    try:
        response = requests.get('https://api.example.com/inflation/india')
        inflation = response.json().get('rate', 5.0)
    except:
        inflation = 5.0  # Fallback value

    # Adjust recommended savings based on inflation
    recommended_savings = savings_goal * (1 + inflation / 100)

    # Generate a message based on savings
    if savings >= savings_goal:
        message = "Great job! You're meeting your savings goal."
    else:
        message = "You need to save more to meet your goal. Consider reducing expenses."

    # Personalized recommendations
    recommendations = []
    if expenses > 0.7 * income:
        recommendations.append("Your expenses are high. Try cutting down on non-essential spending.")
    if savings < 0:
        recommendations.append("You're spending more than you earn. Create a stricter budget.")
    recommendations.append("Consider investing in low-risk options like fixed deposits.")

    # Store the budget entry in history
    budget_entry = {
        'id': len(budget_history) + 1,
        'email': email,
        'income': income,
        'expenses': expenses,
        'savings': savings,
        'savings_goal': savings_goal,
        'recommended_savings': recommended_savings,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    budget_history.append(budget_entry)

    return jsonify({
        'savings': savings,
        'recommended_savings': recommended_savings,
        'inflation': inflation,
        'message': message,
        'recommendations': recommendations
    })

@app.route('/api/budget/history', methods=['POST'])
def get_budget_history():
    data = request.get_json()
    email = data.get('email')
    user_history = [entry for entry in budget_history if entry['email'] == email]
    return jsonify(user_history)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

app = Flask(__name__)
CORS(app)

class BetAnalyzer:
    def __init__(self):
        self.sources = {
            'scores24': 'https://scores24.live',
            '4score': 'https://4score.ru',
            'transfermarkt': 'https://www.transfermarkt.com'
        }
    
    def analyze_football(self, team1, team2, score, time, stats):
        """Анализ футбольного матча по простой системе"""
        try:
            # Парсим счет
            home_score, away_score = map(int, score.split(':'))
            
            # Определяем фаворита
            if home_score > away_score:
                favorite = team1
                favorite_score = home_score
                underdog_score = away_score
            else:
                favorite = team2
                favorite_score = away_score
                underdog_score = home_score
            
            # Анализ по простой системе
            analysis = {
                'match_type': 'football',
                'favorite': favorite,
                'current_score': score,
                'time_elapsed': time,
                'recommendation': None,
                'confidence': 0,
                'reasoning': []
            }
            
            # Критерии для простого анализа
            if favorite_score - underdog_score >= 2:
                if 'control' in stats and stats['control'] > 60:
                    analysis['recommendation'] = 'Победа фаворита'
                    analysis['confidence'] = 80
                    analysis['reasoning'].append(f'Фаворит ведет на {favorite_score - underdog_score} гола')
                    analysis['reasoning'].append(f'Контроль мяча: {stats["control"]}%')
            
            return analysis
            
        except Exception as e:
            return {'error': f'Ошибка анализа: {str(e)}'}
    
    def analyze_tennis(self, player1, player2, sets, current_set):
        """Анализ теннисного матча"""
        try:
            analysis = {
                'match_type': 'tennis',
                'player1': player1,
                'player2': player2,
                'sets': sets,
                'current_set': current_set,
                'recommendation': None,
                'confidence': 0,
                'reasoning': []
            }
            
            # Анализ по простой системе
            if len(sets) >= 1:
                first_set_winner = sets[0]['winner']
                if first_set_winner == player1 and current_set['leader'] == player1:
                    analysis['recommendation'] = f'Победа {player1}'
                    analysis['confidence'] = 75
                    analysis['reasoning'].append(f'{player1} выиграл первый сет')
                    analysis['reasoning'].append(f'{player1} ведет в текущем сете')
            
            return analysis
            
        except Exception as e:
            return {'error': f'Ошибка анализа: {str(e)}'}
    
    def analyze_basketball(self, team1, team2, score, quarter, time):
        """Анализ баскетбольного матча"""
        try:
            home_score, away_score = map(int, score.split(':'))
            
            analysis = {
                'match_type': 'basketball',
                'team1': team1,
                'team2': team2,
                'current_score': score,
                'quarter': quarter,
                'time_remaining': time,
                'recommendation': None,
                'confidence': 0,
                'reasoning': []
            }
            
            # Критерии для простого анализа
            if abs(home_score - away_score) >= 15:
                favorite = team1 if home_score > away_score else team2
                analysis['recommendation'] = f'Победа {favorite}'
                analysis['confidence'] = 70
                analysis['reasoning'].append(f'Отрыв {abs(home_score - away_score)} очков')
                analysis['reasoning'].append(f'Квартал: {quarter}')
            
            return analysis
            
        except Exception as e:
            return {'error': f'Ошибка анализа: {str(e)}'}

# Инициализация анализатора
analyzer = BetAnalyzer()

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_match():
    """API для анализа матча"""
    try:
        data = request.get_json()
        match_type = data.get('type')
        
        if match_type == 'football':
            result = analyzer.analyze_football(
                data.get('team1'),
                data.get('team2'),
                data.get('score'),
                data.get('time'),
                data.get('stats', {})
            )
        elif match_type == 'tennis':
            result = analyzer.analyze_tennis(
                data.get('player1'),
                data.get('player2'),
                data.get('sets', []),
                data.get('current_set', {})
            )
        elif match_type == 'basketball':
            result = analyzer.analyze_basketball(
                data.get('team1'),
                data.get('team2'),
                data.get('score'),
                data.get('quarter'),
                data.get('time')
            )
        else:
            result = {'error': 'Неподдерживаемый тип спорта'}
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Ошибка сервера: {str(e)}'}), 500

@app.route('/api/strategies')
def get_strategies():
    """API для получения стратегий"""
    strategies = {
        'football': [
            {
                'name': 'Доминирующий фаворит',
                'description': 'Фаворит ведет 2+ гола, контроль мяча >60%',
                'bet_type': 'Победа фаворита',
                'confidence': 80
            },
            {
                'name': 'Защитная стена',
                'description': 'Фаворит не пропускает дома 5+ матчей',
                'bet_type': 'Тотал меньше',
                'confidence': 75
            }
        ],
        'tennis': [
            {
                'name': 'Первый сет + преимущество',
                'description': 'Выигран 1-й сет, ведет во 2-м',
                'bet_type': 'Победа в матче',
                'confidence': 75
            }
        ],
        'basketball': [
            {
                'name': 'Квартальное преимущество',
                'description': 'Отрыв 15+ очков в любой четверти',
                'bet_type': 'Победа фаворита',
                'confidence': 70
            }
        ]
    }
    return jsonify(strategies)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
#!/usr/bin/env python3
"""
TrueLiveBet - Простой HTTP сервер для демонстрации
Использует встроенные модули Python
"""

import http.server
import socketserver
import json
import urllib.parse
import os
from datetime import datetime

class BetAnalyzer:
    """Класс для анализа ставок"""
    
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

class TrueLiveBetHandler(http.server.SimpleHTTPRequestHandler):
    """Обработчик запросов для TrueLiveBet"""
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # Читаем HTML файл
            try:
                with open('templates/index.html', 'r', encoding='utf-8') as f:
                    html_content = f.read()
                self.wfile.write(html_content.encode('utf-8'))
            except FileNotFoundError:
                self.wfile.write('HTML файл не найден'.encode('utf-8'))
        elif self.path == '/api/strategies':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            
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
            
            self.wfile.write(json.dumps(strategies, ensure_ascii=False).encode('utf-8'))
        else:
            # Пробуем отдать статические файлы
            try:
                if self.path.startswith('/static/'):
                    file_path = self.path[1:]  # Убираем начальный /
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            content = f.read()
                        
                        # Определяем MIME тип
                        if file_path.endswith('.css'):
                            content_type = 'text/css'
                        elif file_path.endswith('.js'):
                            content_type = 'application/javascript'
                        else:
                            content_type = 'text/plain'
                        
                        self.send_response(200)
                        self.send_header('Content-type', content_type)
                        self.end_headers()
                        self.wfile.write(content)
                        return
            except:
                pass
            
            # Если файл не найден, возвращаем 404
            self.send_error(404, 'Файл не найден')
    
    def do_POST(self):
        """Обработка POST запросов"""
        if self.path == '/api/analyze':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
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
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.end_headers()
                error_response = {'error': f'Ошибка сервера: {str(e)}'}
                self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
        else:
            self.send_error(404, 'API endpoint не найден')

def run_server(port=9000):
    """Запуск сервера"""
    with socketserver.TCPServer(("", port), TrueLiveBetHandler) as httpd:
        print(f"🎯 TrueLiveBet запущен на порту {port}")
        print(f"🌐 Откройте браузер и перейдите по адресу: http://localhost:{port}")
        print("⏹️  Для остановки нажмите Ctrl+C")
        print("-" * 50)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Сервер остановлен")

if __name__ == '__main__':
    run_server()
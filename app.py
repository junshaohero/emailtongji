from flask import Flask, render_template, jsonify, request
import string
import itertools
import time
import json
import logging
import requests
import os
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Namecheap API 配置
NAMECHEAP_API_USER = "albertwang"
NAMECHEAP_API_KEY = "4e28c4ff227b48f3b2f8c3eba7f87a5d"
NAMECHEAP_CLIENT_IP = "127.0.0.1"
NAMECHEAP_API_URL = "https://api.namecheap.com/xml.response"

def generate_combinations(prefix='', length=3, positions=None):
    if positions is None:
        positions = [string.ascii_lowercase for _ in range(length)]
    
    combinations = list(itertools.product(*positions))
    domains = [''.join(combo) + '.ai' for combo in combinations]
    
    return domains

def check_domain_availability(domain):
    try:
        logger.info(f"Checking domain availability for: {domain}.ai")
        
        # 使用 Namecheap API 检查域名
        params = {
            'ApiUser': NAMECHEAP_API_USER,
            'ApiKey': NAMECHEAP_API_KEY,
            'UserName': NAMECHEAP_API_USER,
            'Command': 'namecheap.domains.check',
            'ClientIp': NAMECHEAP_CLIENT_IP,
            'DomainList': f'{domain}.ai'
        }
        
        logger.info(f"Sending request to Namecheap API")
        response = requests.get(
            NAMECHEAP_API_URL,
            params=params,
            timeout=10
        )
        
        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            # 解析 XML 响应
            soup = BeautifulSoup(response.text, 'xml')
            domain_check = soup.find('DomainCheckResult')
            
            if domain_check:
                is_available = domain_check.get('Available', 'false').lower() == 'true'
                
                return {
                    "domain": domain + ".ai",
                    "available": is_available,
                    "status": "success",
                    "whois_url": f"https://who.is/whois/{domain}.ai"
                }
            
        # 如果 API 调用失败，尝试使用备用方法
        backup_url = f'https://www.namecheap.com/domains/registration/results/?domain={domain}.ai'
        backup_response = requests.get(
            backup_url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            },
            timeout=10
        )
        
        if backup_response.status_code == 200:
            # 检查响应文本
            response_text = backup_response.text.lower()
            soup = BeautifulSoup(response_text, 'html.parser')
            
            # 检查特定的 HTML 元素和类来判断域名状态
            unavailable_indicators = [
                'domain-taken',
                'unavailable',
                'already registered',
                'already taken'
            ]
            
            is_available = not any(indicator in response_text for indicator in unavailable_indicators)
            
            return {
                "domain": domain + ".ai",
                "available": is_available,
                "status": "success",
                "whois_url": f"https://who.is/whois/{domain}.ai"
            }
        
        else:
            # 如果备用方法也失败，使用第三种方法
            third_url = f'https://instantdomainsearch.com/domain/{domain}.ai'
            third_response = requests.get(
                third_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'application/json'
                },
                timeout=10
            )
            
            if third_response.status_code == 200:
                try:
                    data = third_response.json()
                    is_available = data.get('isRegistered', True) == False
                except:
                    # 如果 JSON 解析失败，检查响应文本
                    response_text = third_response.text.lower()
                    is_available = 'available' in response_text and 'unavailable' not in response_text
                
                return {
                    "domain": domain + ".ai",
                    "available": is_available,
                    "status": "success",
                    "whois_url": f"https://who.is/whois/{domain}.ai"
                }
            
            else:
                raise Exception("All API attempts failed")
            
    except Exception as e:
        logger.error(f"Error checking domain {domain}.ai: {str(e)}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_domains', methods=['POST'])
def generate_domains():
    data = request.json
    length = data.get('length', 3)
    positions = data.get('positions', [])
    suffix = data.get('suffix', 'ai').strip()
    
    # If no positions specified, use all letters for each position
    if not positions:
        positions = [list(string.ascii_lowercase) for _ in range(length)]
    
    # Generate all possible combinations
    combinations = list(itertools.product(*positions))
    domains = [''.join(combo) + '.' + suffix for combo in combinations]
    
    return jsonify({
        'domains': domains,
        'total': len(domains)
    })

@app.route('/check_domain')
def check_domain():
    try:
        domain = request.args.get('domain', '').lower()
        if not domain or not domain.isalpha() or len(domain) != 3:
            return jsonify({"error": "请输入3个字母的域名"}), 400
        
        result = check_domain_availability(domain)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in check_domain endpoint: {str(e)}")
        return jsonify({
            "domain": domain + ".ai",
            "available": None,
            "status": "error",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)

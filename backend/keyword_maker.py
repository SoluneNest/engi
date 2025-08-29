import openai
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 불용어 리스트 (모두 소문자로 변환)
STOP_WORDS = [
    # 한국어 불용어
    '이', '있', '하', '것', '들', '그', '되', '수', '이', '보', '않', '없', '나', '사람', '주', '아니', '등', '같',
    '우리', '때', '년', '가', '한', '지', '대하', '오', '말', '일', '그렇', '위하',
    '때문', '그것', '두', '말하', '알', '그러나', '그런데', '그래서', '그리고', '또', '더',
    '개', '조', '억', '원', '달러', '만', '명', '위', '월', '일', '시간', '분', '초',
    '뉴스', '기사', '속보', '단독', '종합', '사진', '영상', '헤럴드', '경제', '코리아',
    '아이뉴스24', '전자신문', '지디넷', '디지털데일리', '블로터', '씨넷', 'it',

    # 영어 불용어
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren't", 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
    'can', "can't", 'cannot', 'could', "couldn't", 'did', "didn't", 'do', 'does', "doesn't", 'doing', "don't", 'down', 'during',
    'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn't", 'have', "haven't", 'having', 'he', "he'd", "he'll", "he's",
    'her', 'here', "here's", 'hers', 'herself', 'him', 'himself', 'his', 'how', "how's",
    'i', "i'd", "i'll", "i'm", "i've", 'if', 'in', 'into', 'is', "isn't", 'it', "it's", 'its', 'itself',
    "let's", 'me', 'more', 'most', "mustn't", 'my', 'myself',
    'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own',
    'same', "shan't", 'she', "she'd", "she'll", "she's", 'should', "shouldn't", 'so', 'some', 'such',
    'than', 'that', "that's", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', "there's", 'these', 'they', "they'd",
    "they'll", "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very',
    'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were', "weren't", 'what', "what's", 'when', "when's",
    'where', "where's", 'which', 'while', 'who', "who's", 'whom', 'why', "why's", 'with', "won't', 'would', "wouldn't",
    'you', "you'd", "you'll", "you're", "you've", 'your', 'yours', 'yourself', 'yourselves',
    'news', 'article', 'report', 'inc', 'ltd', 'co', 'llc'
]
# 모든 불용어를 소문자로 변환
STOP_WORDS = [word.lower() for word in STOP_WORDS]


def extract_keywords(text: str) -> List[str]:
    """텍스트에서 키워드를 추출하고 불용어를 제거합니다."""
    if not text or not OPENAI_API_KEY:
        return []
    
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        prompt = f"""
        다음 텍스트에서 핵심 키워드를 추출해주세요. IT/기술 관련 키워드를 우선적으로 선택하고, 
        최대 10개까지 중요한 순서대로 나열해주세요. 각 키워드는 쉼표로 구분하여 반환해주세요.
        
        텍스트: {text[:1000]}
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "당신은 IT/기술 뉴스의 키워드를 추출하는 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.3
        )
        
        keywords_text = response.choices[0].message.content.strip()
        raw_keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]
        
        # 불용어 처리
        filtered_keywords = [
            k for k in raw_keywords 
            if k.lower() not in STOP_WORDS and len(k) > 1
        ]
        
        return filtered_keywords[:8]
        
    except Exception as e:
        print(f"키워드 추출 오류: {e}")
        # 오류 시 기본 키워드 추출 로직 (간단한 방식)
        return extract_simple_keywords(text)

def extract_simple_keywords(text: str) -> List[str]:
    """간단한 키워드 추출 (백업 방식) 및 불용어 처리"""
    keywords = []
    tech_terms = [
        'AI', '인공지능', '머신러닝', '딥러닝', '반도체', '5G', '6G',
        'IoT', '클라우드', '빅데이터', '블록체인', '메타버스', 'VR', 'AR',
        '로봇', '자동화', '스마트팩토리', '디지털전환', 'DX', '핀테크',
        '전기차', '자율주행', '배터리', '태양광', '풍력', '수소',
        '양자컴퓨팅', '사이버보안', '해킹', '랜섬웨어', '개인정보보호',
        '스타트업', '유니콘', '벤처캐피탈', 'IPO', 'M&A'
    ]
    
    text_lower = text.lower()
    for term in tech_terms:
        if term.lower() in text_lower:
            keywords.append(term)
            
    # 불용어 처리
    filtered_keywords = [
        k for k in keywords 
        if k.lower() not in STOP_WORDS and len(k) > 1
    ]
    
    return filtered_keywords[:8]
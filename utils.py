# utils.py
import os
import hashlib
import json
import requests
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
import time
from datetime import datetime
from zhipuai import ZhipuAI
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()
client = ZhipuAI(api_key=os.environ.get("API_KEY"))  # 在这里填写您的智谱AI的API密钥

def calculate_sha256(text):
    """计算字符串的SHA256哈希值。"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def load_cache(key):
    """从缓存中加载数据。"""
    cache_file = os.path.join(CACHE_DIR, f"{key}.json")
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return None
    return None

def save_cache(key, data):
    """将数据保存到缓存。"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f"{key}.json")
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def duckduckgo_search(keywords, max_results=10):
    """使用DuckDuckGo搜索关键词，并返回结果。"""
    url = 'https://api.duckduckgo.com/?q=' + '+'.join(keywords) + '&format=json&pretty=1'
    cache_key = calculate_sha256(url)
    cached_data = load_cache(cache_key)
    if cached_data:
        print("使用缓存数据...")
        return cached_data

    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查是否有错误
        data = response.json()

        results = []
        for item in data.get('RelatedTopics', []):
            if 'Result' in item and 'FirstURL' in item and 'Text' in item:
                results.append({
                    'url': item['FirstURL'],
                    'title': item['Text'].split('</a>')[-1],
                    'text': item['Text'],
                })
            if len(results) >= max_results:
                break

        save_cache(cache_key, results)
        return results

    except requests.RequestException as e:
        print(f"搜索出错: {e}")
        return []

def extract_text_from_url(url):
    """从URL中提取文本内容。"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        # 移除脚本和样式
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        # 清理空格和换行
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text
    except requests.RequestException as e:
        print(f"网页抓取出错: {e}")
        return ""

def llm_analyze(prompt, context=None):
    """调用智谱AI LLM进行分析。"""
    messages = []
    if context:
        messages.append({"role": "user", "content": context})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
        )
        # 检查 API 返回的 usage 信息
        # print(f"API Usage: {response.usage}")
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM调用出错: {e}")
        return ""

def generate_keywords(dimension):
    """使用LLM为研究维度生成关键词。"""
    prompt = f"为研究维度「{dimension}」生成5-7个高度相关的搜索关键词，关键词之间用空格分隔。"
    response = llm_analyze(prompt)
    # 假设LLM返回的关键词是用空格分隔的
    return response.split()

def process_data(search_results):
    """清洗数据并生成摘要。"""
    all_text = ""
    for result in search_results:
        text = extract_text_from_url(result['url'])
        all_text += text + "\n"

    if not all_text:
        return ""

    # 使用LLM进行摘要
    prompt = "请为以下文本生成一个简明扼要的摘要：\n" + all_text[:5000]  # 限制长度
    summary = llm_analyze(prompt)
    return summary

def build_knowledge_graph(all_data):
    """构建知识图谱（简化版，仅为示例）。"""
    # 这里可以根据实际需求进行更复杂的知识图谱构建
    # 例如使用spaCy进行实体识别和关系抽取
    knowledge_graph = {}
    for dimension, data in all_data.items():
        prompt = f"从以下文本中提取关键实体和关系，研究维度为「{dimension}」：\n{data}"
        response = llm_analyze(prompt)
        knowledge_graph[dimension] = response
    return knowledge_graph

def initialize_report():
    """初始化报告结构。"""
    return {
        "title": "",
        "introduction": "",
        "sections": {},
        "conclusion": "",
        "references": []
    }

def llm_generate_section(section_data):
    """使用LLM生成报告章节草稿。"""
    prompt = f"根据以下信息，撰写报告的一个章节：\n{section_data}"
    draft = llm_analyze(prompt)
    return draft

def integrate_content(report, draft):
    """将草稿整合到报告中。"""
    # 这里可以根据实际需求进行更复杂的整合逻辑
    report['sections'][len(report['sections']) + 1] = draft
    return report

def llm_validate(context, prompt):
    """使用LLM进行验证。"""
    response = llm_analyze(prompt, context=context)
    # 假设LLM返回一个包含 "needs_search" (bool) 和 "search_clues" (list) 的字典
    # 这里需要根据实际LLM的输出进行解析
    try:
        # 尝试解析JSON格式的响应
        validation_result = json.loads(response)
        return validation_result
    except json.JSONDecodeError:
        print("LLM返回的验证结果不是有效的JSON格式。")
        return {"needs_search": False, "search_clues": []}

def supplementary_search(search_clues):
    """根据验证结果进行补充搜索。"""
    for clue in search_clues:
        keywords = generate_keywords(clue)
        search_results = duckduckgo_search(keywords)
        cleaned_data = process_data(search_results)
        # 将补充搜索的结果添加到相关章节或知识图谱中
        print(f"补充搜索「{clue}」的结果：{cleaned_data}")

def quality_check(report):
    """最终质量检查。"""
    prompt = "请对以下报告进行全面质量评估，包括数据准确性、逻辑连贯性、语言流畅性等方面，并提出改进建议：\n" + json.dumps(report, ensure_ascii=False)
    response = llm_analyze(prompt)
    report['quality_check'] = response
    return report

def assess_credibility(source):
    """评估信息来源的可信度（简化版）。"""
    # 可以根据域名、发布者等信息进行评估
    # 这里仅作示例
    if "wikipedia.org" in source:
        return "high"
    elif ".gov" in source or ".edu" in source:
        return "high"
    else:
        return "medium"

def check_data_recency(text):
    """检查数据时效性（简化版）。"""
    # 可以通过正则表达式等方式查找日期信息
    # 这里仅作示例
    today = datetime.now()
    # 查找年份
    years = [int(year) for year in re.findall(r'\b(19|20)\d{2}\b', text)]
    if years:
        latest_year = max(years)
        if today.year - latest_year > 5:
            return "outdated"
    return "recent"

def detect_contradictions(data):
    """检测信息矛盾（简化版）。"""
    # 可以通过比较不同来源的信息进行检测
    # 这里仅作示例
    sentences = sent_tokenize(data)
    contradictions = []
    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            prompt = f"判断以下两句话是否存在逻辑矛盾：\n1. {sentences[i]}\n2. {sentences[j]}"
            response = llm_analyze(prompt)
            if "存在矛盾" in response:  # 简单的判断
                contradictions.append((sentences[i], sentences[j]))
    return contradictions

import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER

def generate_pdf_report(report, filename="research_report.pdf"):
    """生成PDF格式的报告。"""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # 添加标题
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontSize=24,
        spaceAfter=20
    )
    story.append(Paragraph(report.get('title', '研究报告'), title_style))

    # 添加引言
    introduction_style = ParagraphStyle(
        'IntroductionStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=15
    )
    story.append(Paragraph(report.get('introduction', '无引言'), introduction_style))

    # 添加章节
    section_heading_style = ParagraphStyle(
        'SectionHeadingStyle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=15,
        spaceAfter=10
    )
    section_body_style = ParagraphStyle(
        'SectionBodyStyle',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10,
        alignment=TA_JUSTIFY
    )

    for section_num, section_content in report.get('sections', {}).items():
        story.append(Paragraph(f"第{section_num}部分", section_heading_style))
        story.append(Paragraph(section_content, section_body_style))

    # 添加结论
    conclusion_style = ParagraphStyle(
        'ConclusionStyle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=15,
        spaceAfter=10
    )
    story.append(Paragraph("结论", conclusion_style))
    story.append(Paragraph(report.get('conclusion', '无结论'), section_body_style))

    # 添加参考文献（简化版）
    references_style = ParagraphStyle(
        'ReferencesStyle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=15,
        spaceAfter=10
    )
    story.append(Paragraph("参考文献", references_style))
    for ref in report.get('references', []):
        story.append(Paragraph(ref, section_body_style))

    # 添加质量检查部分
    quality_check_style = ParagraphStyle(
        'QualityCheckStyle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=15,
        spaceAfter=10
    )
    story.append(Paragraph("质量检查", quality_check_style))
    story.append(Paragraph(report.get('quality_check', '无质量检查结果'), section_body_style))

    doc.build(story)
    print(f"PDF报告已生成：{filename}")


import os
import json
import base64
import requests
from bs4 import BeautifulSoup

# 获取 GitHub Star 数
def get_github_stars(repo_url):
    api_url = repo_url.replace('https://github.com/', 'https://api.github.com/repos/')
    response = requests.get(api_url)
    data = response.json()
    return data['stargazers_count']

# 获取 Google Scholar 引用次数
def get_citation_count(scholar_url):
    response = requests.get(scholar_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    citations = soup.find_all('div', class_='gs_ri')[0].find('div', class_='gs_fl').find_all('a')[2].text
    return int(citations.split(' ')[-1])

# 读取 README.md
with open('README.md', 'r') as file:
    readme_content = file.readlines()

# 更新论文列表
updated_readme = []
in_paper_list = False

for line in readme_content:
    if line.startswith('- **'):
        in_paper_list = True
        # 解析行中的信息
        parts = line.split('|')
        title_part = parts[0].strip()
        pdf_link = parts[1].strip().split('](')[-1].strip(')')
        code_link = parts[2].strip().split('](')[-1].strip(')')
        github_link = parts[3].strip().split('](')[-1].strip(')')
        citation_count = parts[4].strip().split(' ')[-1]

        # 获取最新的 GitHub Star 数和引用次数
        github_stars = get_github_stars(github_link)
        citations = get_citation_count(pdf_link)

        # 重新构建行
        new_line = f"- {title_part} | [PDF 链接]({pdf_link}) | [代码链接]({code_link}) | GitHub Star 数: ![GitHub stars](https://img.shields.io/badge/stars-{github_stars}-brightgreen) | 引用次数: ![Citation count](https://img.shields.io/badge/citations-{citations}-blue)\n"
        updated_readme.append(new_line)
    else:
        if in_paper_list and line.strip() == '':
            in_paper_list = False
        updated_readme.append(line)

# 获取新论文数据
issue_body = os.getenv('GITHUB_ISSUE_BODY')
if issue_body:
    paper_data = json.loads(issue_body)
    # 获取新论文的 GitHub Star 数和引用次数
    github_stars = get_github_stars(paper_data['github'])
    citations = get_citation_count(paper_data['pdf'])

    # 在论文列表末尾添加新论文
    new_paper_md = f"- **{paper_data['title']}**: [PDF 链接]({paper_data['pdf']}) | [代码链接]({paper_data['code']}) | GitHub Star 数: ![GitHub stars](https://img.shields.io/badge/stars-{github_stars}-brightgreen) | 引用次数: ![Citation count](https://img.shields.io/badge/citations-{citations}-blue)\n"
    updated_readme.append(new_paper_md)

# 更新 README.md
with open('README.md', 'w') as file:
    file.writelines(updated_readme)

# 通过 API 提交更改
headers = {
    'Authorization': f'token {os.getenv("GITHUB_TOKEN")}',
    'Content-Type': 'application/json'
}
data = {
    'message': 'Update paper list',
    'content': base64.b64encode(open('README.md', 'rb').read()).decode('utf-8'),
    'branch': 'main'
}
response = requests.put(
    f'https://api.github.com/repos/{os.getenv("GITHUB_REPOSITORY")}/contents/README.md',
    headers=headers,
    data=json.dumps(data)
)
response.raise_for_status()

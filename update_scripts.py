import requests
from bs4 import BeautifulSoup

# 获取 Google Scholar 引用次数
def get_citation_count(scholar_url):
    response = requests.get(scholar_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    citations = soup.find_all('div', class_='gs_ri')[0].find('div', class_='gs_fl').find_all('a')[2].text
    return int(citations.split(' ')[-1])

# 更新 README.md
def update_readme(citation_counts):
    with open('README.md', 'r') as file:
        readme_content = file.readlines()
    
    for i, line in enumerate(readme_content):
        if '引用次数' in line:
            paper_index = line.split(' ')[-1].strip()
            new_citation_line = f'- **引用次数**: ![Citation count](https://img.shields.io/badge/citations-{citation_counts[paper_index]}-blue)\n'
            readme_content[i] = new_citation_line
    
    with open('README.md', 'w') as file:
        file.writelines(readme_content)

# 示例调用
citation_counts = {'论文1': get_citation_count('Google Scholar URL 1'), '论文2': get_citation_count('Google Scholar URL 2')}
update_readme(citation_counts)

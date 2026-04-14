#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号文章批量处理脚本
"""

import os
import subprocess
import time
from PIL import Image
import pytesseract

def download_images(article_urls, article_index, output_base_dir):
    """下载文章的所有图片"""
    print(f"\n{'='*60}")
    print(f"开始处理第 {article_index} 篇文章")
    print(f"{'='*60}\n")
    
    # 使用 playwright 获取图片
    playwright_open_cmd = f"playwright-cli open \"{article_urls[0]}\""
    subprocess.run(playwright_open_cmd, shell=True, capture_output=True)
    
    time.sleep(3)  # 等待页面加载
    
    # 获取图片 URLs
    get_images_cmd = """
    playwright-cli eval "Array.from(document.querySelectorAll('img')).filter(img => img.src.includes('mmbiz')).map(img => img.src).join('\\n')"
    """
    result = subprocess.run(get_images_cmd, shell=True, capture_output=True, text=True)
    image_urls = result.stdout.strip().split('\n')
    
    # 过滤掉无关的图片
    image_urls = [url for url in image_urls if url and 'mmbiz' in url and 'wxfrom=12' in url]
    
    # 去重
    image_urls = list(dict.fromkeys(image_urls))
    
    print(f"找到 {len(image_urls)} 张图片\n")
    
    # 下载图片
    output_dir = os.path.join(output_base_dir, f"article_{article_index}")
    os.makedirs(output_dir, exist_ok=True)
    
    for i, url in enumerate(image_urls, 1):
        filename = f"article_{article_index}_{i}.png"
        filepath = os.path.join(output_dir, filename)
        
        print(f"下载图片 {i}/{len(image_urls)}: {filename}")
        subprocess.run([
            "curl", "-L", "-o", filepath, url
        ], capture_output=True)
        
    print(f"\n✅ 所有图片已保存到: {output_dir}\n")
    
    # 关闭浏览器
    subprocess.run("playwright-cli close", shell=True, capture_output=True)
    
    return image_urls

def ocr_extract(images_dir, article_index, article_title, article_url, output_file):
    """使用 OCR 提取图片中的文字"""
    print(f"开始 OCR 识别...\n")
    
    md_content = []
    md_content.append(f"# {article_title}")
    md_content.append("")
    md_content.append(f"**原文链接**: {article_url}")
    md_content.append("")
    md_content.append("---")
    md_content.append("")
    md_content.append("*以下内容通过 OCR 从图片中提取，可能存在识别错误*")
    md_content.append("")
    
    # 获取所有图片文件
    image_files = sorted([f for f in os.listdir(images_dir) if f.startswith(f'article_{article_index}_') and f.endswith('.png')])
    
    for i, image_file in enumerate(image_files, 1):
        image_path = os.path.join(images_dir, image_file)
        
        print(f"正在处理图片 {i}/{len(image_files)}: {image_file}")
        
        try:
            # 使用 tesseract 提取文字
            text = pytesseract.image_to_string(Image.open(image_path), lang='chi_sim+eng')
            
            # 清理文字
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            md_content.append(f"## 第 {i} 部分")
            md_content.append("")
            for line in lines:
                md_content.append(line)
            md_content.append("")
            md_content.append("---")
            md_content.append("")
            
            print(f"✅ 已提取 {len(lines)} 行文字")
        except Exception as e:
            print(f"❌ 处理失败: {e}")
            md_content.append(f"## 第 {i} 部分")
            md_content.append("")
            md_content.append("*图片识别失败*")
            md_content.append("")
            md_content.append("---")
            md_content.append("")
    
    # 写入 Markdown 文件
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_content))
    
    print(f"\n✅ 已生成文字版 Markdown: {output_file}")
    print(f"📊 共处理 {len(image_files)} 张图片\n")

def main():
    """主函数"""
    # 剩余的文章列表
    articles = [
        {
            "index": 3,
            "url": "https://mp.weixin.qq.com/s/8wT3pkzvei98yJHZCqITHg",
            "title": "前端 AI 面试题"
        },
        {
            "index": 4,
            "url": "https://mp.weixin.qq.com/s/u1uld9p0HJErZee3VdjaoA",
            "title": "前端 AI 面试题"
        },
        {
            "index": 5,
            "url": "https://mp.weixin.qq.com/s/cwV9fa_z0ZnzJQwdC81SIg",
            "title": "前端 AI 面试题"
        },
    ]
    
    output_base_dir = "/Users/lukejyhuang/WorkBuddy/Claw/images"
    
    for article in articles:
        article_index = article["index"]
        article_url = article["url"]
        article_title = article["title"]
        
        # 下载图片
        download_images([article_url], article_index, output_base_dir)
        
        # OCR 提取
        images_dir = os.path.join(output_base_dir, f"article_{article_index}")
        output_file = f"/Users/lukejyhuang/WorkBuddy/Claw/articles/article_{article_index}.md"
        ocr_extract(images_dir, article_index, article_title, article_url, output_file)
        
        time.sleep(2)  # 短暂休息
    
    print("\n" + "="*60)
    print("🎉 所有文章处理完成！")
    print("="*60)

if __name__ == "__main__":
    main()

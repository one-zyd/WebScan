> ## Python 多线程 Web **目录扫描器** (Beginner-friendly)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


这是一个纯 Python 编写的、基于多线程的 Web 目录扫描器。作为一个网络安全和 Python 初学者，这是我的第一个从零手敲的实战项目。在此记录完整的开发思路、底层原理解析以及踩坑日记。

## 免责声明

**本工具仅供网络安全学习和本地授权靶场（如 DVWA、Pikachu）测试使用。**
未经授权对任何真实公网网站进行扫描、探测属于**违法行为**，请务必遵守《中华人民共和国网络安全法》。开发者不承担任何因滥用此工具而产生的法律责任。

---


## 功能特性

- **多线程并发**：使用 `ThreadPoolExecutor` 线程池，相比单线程大幅提升扫描速度。
- **容错**：采用 Python 的 EAFP 哲学，程序遇到死胡同、连接超时绝不会崩溃闪退。
- **命令行参数化**：使用 `argparse` 模块，支持灵活指定目标 URL、字典路径和线程数。
- **伪装请求头**：自带 `User-Agent` 伪装，并屏蔽了 `urllib3` 证书警告。

---

## 环境安装

* **Python 3.8+**


---

## 踩坑记录

- **python函数及语法问题**
- **关于请求头伪造：** 在Edge或Chrome浏览器中打开 *网页* -> 开发者工具 -> 网络(Network) -> 找到 请求标头 (Request Headers) 区域，写到程序中用requests申请的请求头中。也可以自己多用几个浏览器建一个UA池，并引入random库，申请的时候随机用UA头，降低暴露风险。
- **关于ThreadPoolExecutor多线程：** 其中executor不像传统函数写法，其第一个参数一定是纯函数名，应该是 *executor.submit(scan_url,args.url,path)* ,而不是 ~~executor.submit(scan_url(args.url,path))~~ 。
- **关于不加-u -w:** 由于parser定义时required=True，不写会出现argparse给出的SystemExit错误，也可以用try尝试捕获错误，但是记得sys.exit().
- **关于我自己理解的程序顺序：** 由于主网站和拼接的路径会重复操作，所以要单独写一个函数来做这件事。有了scan_url函数之后：
  - 搭建类似sqlmap操作方式的parser 
  - 查找输入的字典（ *这里考虑到用户输入或记忆错误，用try尝试捕获错误，后终止。* ） 
  - 输出基本参数及页面 
  - 构造ThreadPoolExecutor多线程执行任务并扫描执行scan_url函数 
  - 结束
  
---

## 最后代码如下

``` python
import requests
import sys
import argparse
from concurrent.futures import ThreadPoolExecutor
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS =  {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def scan_url(base_url,path) :
    target_url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    try :
        response = requests.get(target_url,headers=HEADERS,timeout=3,verify=False,allow_redirects=False)
        if response.status_code in [200,301,302,403] :
            print(f"Found: {response.status_code:3} | Length: {len(response.content):5} | {target_url}")
    except requests.exceptions.RequestException :
        pass

def main():
    parser = argparse.ArgumentParser(description="Python多线程web目录扫描器")
    parser.add_argument("-u","--url",required=True,help="目标URL（例如：http://example.com）")
    parser.add_argument("-w","--wordlist",required=True,help="字典文件路径（例如：dict.txt）")
    parser.add_argument("-t","--threads",default=10,type=int,help="线程数（默认：10）")
    args = parser.parse_args()

    try:
        with open(args.wordlist,'r',encoding='utf-8') as f:
            paths = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"错误：找不到字典文件 {args.wordlist}")
        sys.exit(1)

    print(f"目标 URL：{args.url}")
    print(f"字典大小：{len(paths)} 条")
    print(f"线程数量：{args.threads}")
    print('-' * 50)
    
    with ThreadPoolExecutor(max_workers=args.threads) as executor :
        for path in paths :
            executor.submit(scan_url,args.url,path)

    print('-' * 50)
    print("扫描完成！")

if __name__ == "__main__":
    main()

```

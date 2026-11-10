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

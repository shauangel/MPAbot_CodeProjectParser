from googlesearch import search


# 輸入參數關鍵字string array、一次需回傳筆數、第幾頁
def outer_search(keywords, result_num, page_num):
    separator = " "
    query = separator.join(keywords) + " site:codeproject.com"
    temp = [i for i in search(query, tld="com", num=result_num*2, start=result_num * page_num, stop=result_num*2, pause=0.1)]
    result = [r for r in temp if "/Questions" in r]
    return result[:result_num]
# pause (float) – Lapse to wait between HTTP requests. A lapse too long will make the search slow, but a lapse too short may cause Google to block your IP. Your mileage may vary!


if __name__ == "__main__":
    result = outer_search(['python', 'app', 'CORS', 'error'], 10, 0)
    for i in result:
        print(i)
import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime

project_link = "https://github.com/Li732375/weather_diary"
#API_KEY = "YOUR_API_KEY"  # 從 GitHub Secrets 設定
ElementName_list = ["溫度", "體感溫度", "相對濕度", "降雨機率"]

# 獲取天氣資料
def get_weather_data():
    URL = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-065?Authorization={API_KEY}&ElementName={",".join(ElementName_list)}&format=JSON&sort=time"

    response = requests.get(URL)
    data = response.json()

    # 儲存 JSON 結果
    with open("KS_3day_weather_forecast_data.json", "w", encoding="utf-8-sig") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data

# 繪製每小時單位變化的數據
def get_trend_values(Loc_data, index):
    """
    :param data: 載入的 JSON 資料
    :param index: 輸出的圖片檔名序號
    """

    for element in Loc_data["WeatherElement"]:
        WeatherElement_Name_zh = element["ElementName"]  # 氣象單位繁中名稱
        WeatherElement_Name = ""  # 氣象單位英文名稱  
        # 單位的時段資料
        temperature_times = []
        temperature_values = []
        # 同區域所有圖片檔名
        Loc_Table_Names = []

        # 擷取各時段單位數據
        for time_info in element["Time"]:
            dt = datetime.fromisoformat(time_info["DataTime"])
            time_label = dt.strftime("%m/%d %H")  # ex：04/28 12、04/28 13...
            WeatherElement_Name = list(time_info["ElementValue"][0].keys())[0]  # 取得氣象單位英文名稱
            WeatherElement_value = list(time_info["ElementValue"][0].values())[0]  # 取得氣象單位數值
            
            temperature_times.append(time_label)
            temperature_values.append(int(WeatherElement_value))

        # 繪表
        table_address = plot_table(Loc_data["LocationName"], 
                                    WeatherElement_Name_zh, 
                                    WeatherElement_Name, 
                                    temperature_times, 
                                    temperature_values, 
                                    index)
        Loc_Table_Names.append(table_address)
        
    return Loc_data["LocationName"], Loc_Table_Names

# 繪製折線圖
def plot_table(loc_name, WeatherElement_Name_zh, WeatherElement_Name, temp_times, temp_values, index):
    plt.rcParams['font.family'] = 'Microsoft JhengHei' # 設置中文字體
    plt.style.use('dark_background')  # 背景黑色
    fig, ax = plt.subplots(figsize=(14, 6))

    ax.plot(temp_times, temp_values, marker="o", linestyle="-", color="cyan", linewidth=2)  # 線條亮色+粗一點

    # 在每個點上標溫度數值
    for x, y in zip(temp_times, temp_values):
        ax.text(x, y + 0.3, f"{y:.0f}", ha='center', va='bottom', fontsize=12, color='white')

    # 設定標題和軸
    ax.set_title(f"{loc_name} 每小時{WeatherElement_Name_zh}變化", fontsize=16)
    ax.set_xlabel("時 (Hour)", fontsize=12)
    ax.set_ylabel(f"{WeatherElement_Name_zh}", fontsize=12)

    ax.set_xticks(temp_times)  # 只顯示有資料的時刻
    ax.grid(True, linestyle='--', alpha=0.5)

    # 儲存成圖片
    plt.tight_layout()
    save_link = f"Tables/{date}_{WeatherElement_Name}_{index}.png"
    plt.savefig(save_link, dpi=300)
    plt.close()

    return save_link  # 回傳圖片路徑


if __name__ == "__main__":
    # 取得時間
    date = datetime.now().strftime("%Y-%m-%d")

    with open("weather.md", "w", encoding="utf-8-sig") as f:
        f.write(f"\# {date} 高雄天氣預報\n\n")
        f.write(f"一個託付的每日自動更新氣象資料的專案\n\n")
        f.write(f"|區里|預報圖|\n")
        f.write(f"|:-:|:-:|\n")

    data = get_weather_data()
    loc_list = data["records"]["Locations"][0]["Location"]
    for index, loc in enumerate(loc_list):
        # 繪製每小時變化的折線圖並儲存成圖片
        Location_Name, Table_links = get_trend_values(loc, index)

        for links in Table_links:
            with open("weather.md", "a", encoding="utf-8-sig") as f:
                pic_link = project_link + "/" + links
                f.write(f"|{Location_Name}|![該區每小時變化圖]({pic_link})|\n")

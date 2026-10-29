"""使用 PyScript / Pyodide 在 iPhone Safari 執行的網路收音機。"""
from js import document, window
from pyodide.ffi import create_proxy

# 網路電台串流：SomaFM 公開提供的 128 kbps MP3 串流
STATIONS = [
    {"name": "ICRT FM100", "desc": "英文新聞與流行音樂","url": "url": "https://stream.rcs.revma.com/nkdfurztxp3vv"},
    {"name": "中廣音樂網", "desc": "i Radio · 流行音樂", "url": "https://stream.rcs.revma.com/ndk05tyy2tzuv"},
    {"name": "中廣流行網", "desc": "I like radio · 流行與談話", "url": "https://stream.rcs.revma.com/aw9uqyxy2tzuv"},
    {"name": "中廣新聞網", "desc": "新聞與時事", "url": "https://stream.rcs.revma.com/78fm9wyy2tzuv"},
    {"name": "警廣全國交通網", "desc": "交通路況與治安資訊", "url": "https://stream.pbs.gov.tw/live/PBS/playlist.m3u8"},
    {"name": "警廣臺中分臺", "desc": "臺中地區廣播", "url": "https://stream.pbs.gov.tw/live/TCS/playlist.m3u8"},
    {"name": "Hit FM 線上收聽", "desc": "點下方連結開啟官方播放器", "url": None, "website": "https://www.hitfm.com.tw/mobile/onair.php"},
   
]


index = 0
playing = False
audio = document.getElementById("audio")
name_label = document.getElementById("station-name")
desc_label = document.getElementById("station-desc")
status_label = document.getElementById("status")
play_button = document.getElementById("play")
selector = document.getElementById("stations")
external_link = document.getElementById("external-link")


def status(message):
    status_label.textContent = message


def fill_selector():
    selector.innerHTML = ""
    for i, station in enumerate(STATIONS):
        option = document.createElement("option")
        option.value = str(i)
        option.textContent = station["name"]
        selector.appendChild(option)


def show_station():
    current = STATIONS[index]
    name_label.textContent = current["name"]
    desc_label.textContent = current["desc"]
    selector.value = str(index)
    if current.get("website"):
        external_link.href = current["website"]
        external_link.style.display = "block"
    else:
        external_link.style.display = "none"


def stop():
    global playing
    audio.pause()
    playing = False
    play_button.textContent = "▶"
    status("已暫停")


def start():
    global playing
    current = STATIONS[index]
    if not current.get("url"):
        status("此電台使用官方網站播放，請點下方連結")
        return
    if audio.src != current["url"]:
        audio.src = current["url"]
    status("正在連線…")
    try:
        # browser audio.play() 回傳 Promise；如失敗會由 error event 顯示提示
        promise = audio.play()
        # 留存 proxy，避免 Pyodide 回收非同步錯誤處理器
        reject_handler = create_proxy(lambda err: status("播放失敗，請檢查串流網址或網路"))
        handlers.append(reject_handler)
        promise.catch(reject_handler)
        playing = True
        play_button.textContent = "⏸"
    except Exception:
        status("無法播放，請手動點擊播放鍵")


def choose(new_index, autoplay=False):
    global index
    stop()
    index = new_index % len(STATIONS)
    audio.removeAttribute("src")
    audio.load()
    show_station()
    status("已選擇電台，按 ▶ 播放")
    if autoplay:
        start()


def on_play(event):
    if audio.paused:
        start()
    else:
        stop()


def on_prev(event):
    was_playing = not audio.paused
    choose(index - 1, autoplay=was_playing)


def on_next(event):
    was_playing = not audio.paused
    choose(index + 1, autoplay=was_playing)


def on_select(event):
    was_playing = not audio.paused
    choose(int(selector.value), autoplay=was_playing)


def on_volume(event):
    try:
        audio.volume = float(event.target.value) / 100
    except Exception:
        pass


def on_add(event):
    url = str(document.getElementById("custom").value).strip()
    if not url.startswith("https://"):
        status("請輸入以 https:// 開頭的串流網址")
        return
    STATIONS.append({"name": f"自訂電台 {len(STATIONS) - 5}", "desc": "自訂網路串流", "url": url})
    fill_selector()
    choose(len(STATIONS) - 1)
    document.getElementById("custom").value = ""


def on_error(event):
    global playing
    playing = False
    play_button.textContent = "▶"
    status("串流連線失敗，請切換電台或開啟官方播放器")


# 保留代理物件參照，避免 Python callback 被回收
handlers = []
for element_id, event_name, callback in [
    ("play", "click", on_play),
    ("prev", "click", on_prev),
    ("next", "click", on_next),
    ("stations", "change", on_select),
    ("volume", "input", on_volume),
    ("add", "click", on_add),
    ("audio", "error", on_error),
]:
    proxy = create_proxy(callback)
    handlers.append(proxy)
    document.getElementById(element_id).addEventListener(event_name, proxy)

fill_selector()
show_station()
status("準備完成，按 ▶ 開始收聽")

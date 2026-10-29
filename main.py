"""使用 PyScript / Pyodide 在 iPhone Safari 執行的網路收音機。"""
from js import document, window
from pyodide.ffi import create_proxy

# 網路電台串流：SomaFM 公開提供的 128 kbps MP3 串流
STATIONS = [
    {"name": "Groove Salad", "desc": "輕鬆電音 / Downtempo", "url": "https://ice2.somafm.com/groovesalad-128-mp3"},
    {"name": "Drone Zone", "desc": "氛圍音樂 / Ambient", "url": "https://ice2.somafm.com/dronezone-128-mp3"},
    {"name": "Deep Space One", "desc": "宇宙氛圍 / Space Ambient", "url": "https://ice2.somafm.com/deepspaceone-128-mp3"},
    {"name": "Secret Agent", "desc": "間諜電影配樂 / Lounge", "url": "https://ice2.somafm.com/secretagent-128-mp3"},
]

index = 0
playing = False
audio = document.getElementById("audio")
name_label = document.getElementById("station-name")
desc_label = document.getElementById("station-desc")
status_label = document.getElementById("status")
play_button = document.getElementById("play")
selector = document.getElementById("stations")


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


def stop():
    global playing
    audio.pause()
    playing = False
    play_button.textContent = "▶"
    status("已暫停")


def start():
    global playing
    current = STATIONS[index]
    if audio.src != current["url"]:
        audio.src = current["url"]
    status("正在連線…")
    try:
        # browser audio.play() 回傳 Promise；如失敗會由 error event 顯示提示
        promise = audio.play()
        promise.catch(create_proxy(lambda err: status("播放失敗，請檢查串流網址或網路")))
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
    choose(index - 1, autoplay=not audio.paused)


def on_next(event):
    choose(index + 1, autoplay=not audio.paused)


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
    STATIONS.append({"name": f"自訂電台 {len(STATIONS) - 3}", "desc": "自訂網路串流", "url": url})
    fill_selector()
    choose(len(STATIONS) - 1)
    document.getElementById("custom").value = ""


def on_error(event):
    global playing
    playing = False
    play_button.textContent = "▶"
    status("串流連線失敗，請切換電台或檢查網路")


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

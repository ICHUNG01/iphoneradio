# iPhone Python 網路收音機

使用 PyScript + Python + HTML Audio 寫成，可在 iPhone Safari 操作，不是原生 FM 接收器。

## 使用
1. 把 index.html 與 main.py 放在同一個 GitHub repository 根目錄。
2. Settings -> Pages -> Deploy from a branch -> main / (root)，儲存。
3. 用 iPhone Safari 打開 GitHub Pages 提供的 HTTPS 網址。
4. 點擊播放。Safari 分享 -> 加入主畫面，可作為網頁 App 使用。

## 本機測試
請在這個資料夾執行 `python -m http.server 8000`，然後在電腦瀏覽器進入 http://localhost:8000。不要用 file:// 直接打開 index.html，否則可能無法載入 main.py。

## 注意
- PyScript 和廣播串流都需要網路。
- iOS 對網頁音量控制有限制，可使用側邊音量鍵。
- 背景播放取決於 iOS/Safari 行為，不保證永久播放。
- 自訂網址需是 HTTPS 可播放的串流，而非廣播網站首頁。

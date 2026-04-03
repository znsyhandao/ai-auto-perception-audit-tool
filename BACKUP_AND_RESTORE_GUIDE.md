# 馃攧 OpenClaw娴嬭瘯妗嗘灦澶囦唤涓庢仮澶嶆寚鍗?
## 馃幆 鏍稿績闂

### 闂锛?**OpenClaw宸ヤ綔绌洪棿 (`~/.openclaw/workspace/`) 鍦ㄩ噸鏂板畨瑁匫penClaw鏃朵細琚竻绌猴紒**

### 褰卞搷锛?- 鉂?`TESTING_FRAMEWORK.md` - 涓㈠け
- 鉂?`security_scanner.py` - 涓㈠け  
- 鉂?`release_checklist.py` - 涓㈠け
- 鉂?璁板繂鏂囦欢 - 涓㈠け
- 鉂?鎵€鏈夋祴璇曞拰瀹夊叏娴佺▼ - 涓㈠け

### 瑙ｅ喅鏂规锛?**寤虹珛鐙珛鐨勫浠界郴缁燂紝纭繚娴嬭瘯妗嗘灦姘镐箙鍙敤**

## 馃搧 澶囦唤绯荤粺鏋舵瀯

### 1. 涓诲浠戒綅缃紙鎺ㄨ崘锛夛細
```
C:\Users\<鐢ㄦ埛鍚?\OpenClaw_TestingFramework\
鈹溾攢鈹€ TESTING_FRAMEWORK.md          # 娴嬭瘯妗嗘灦鏂囨。
鈹溾攢鈹€ security_scanner.py           # 瀹夊叏妫€鏌ヨ剼鏈?鈹溾攢鈹€ release_checklist.py          # 鍙戝竷妫€鏌ユ竻鍗?鈹溾攢鈹€ memory\2026-03-23.md          # 瀹夊叏鏁欒璁板綍
鈹溾攢鈹€ MEMORY.md                     # 闀挎湡璁板繂
鈹溾攢鈹€ restore_testing_framework.py  # 鎭㈠鑴氭湰
鈹溾攢鈹€ auto_load_testing.py          # 鑷姩鍔犺浇鍣?鈹斺攢鈹€ BACKUP_AND_RESTORE_GUIDE.md   # 鏈寚鍗?```

### 2. 鍙€夊浠戒綅缃紙澶氫綅缃浠斤級锛?- **浜戝瓨鍌?*锛歄neDrive銆丟oogle Drive銆丏ropbox
- **鐗堟湰鎺у埗**锛欸itHub銆丟itLab銆丅itbucket
- **澶栭儴瀛樺偍**锛歎SB椹卞姩鍣ㄣ€丯AS
- **鍏朵粬鐩綍**锛歚D:\Backups\OpenClaw\`

## 馃敡 澶囦唤鏂规硶

### 鏂规硶1锛氭墜鍔ㄥ浠斤紙绔嬪嵆鎵ц锛?```powershell
# 1. 鍒涘缓澶囦唤鐩綍
mkdir D:\\OpenClaw_TestingFramework

# 2. 澶嶅埗鎵€鏈夋枃浠?Copy-Item "C:\Users\cqs10\.openclaw\workspace\TESTING_FRAMEWORK.md" "D:\\OpenClaw_TestingFramework\" -Force
Copy-Item "C:\Users\cqs10\.openclaw\workspace\security_scanner.py" "D:\\OpenClaw_TestingFramework\" -Force
Copy-Item "C:\Users\cqs10\.openclaw\workspace\release_checklist.py" "D:\\OpenClaw_TestingFramework\" -Force
Copy-Item "C:\Users\cqs10\.openclaw\workspace\memory\2026-03-23.md" "D:\\OpenClaw_TestingFramework\memory\" -Force
Copy-Item "C:\Users\cqs10\.openclaw\workspace\MEMORY.md" "D:\\OpenClaw_TestingFramework\" -Force
```

### 鏂规硶2锛氫娇鐢ㄦ仮澶嶈剼鏈浠?```bash
# 杩愯鎭㈠鑴氭湰锛堜篃浼氬垱寤哄浠斤級
python D:\\OpenClaw_TestingFramework\restore_testing_framework.py
```

### 鏂规硶3锛氳嚜鍔ㄥ浠斤紙璁″垝浠诲姟锛?```powershell
# 鍒涘缓姣忔棩澶囦唤浠诲姟
$action = New-ScheduledTaskAction -Execute "PowerShell" -Argument "-File C:\Users\cqs10\backup_testing_framework.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At "02:00"
Register-ScheduledTask -TaskName "OpenClawTestFrameworkBackup" -Action $action -Trigger $trigger -Description "姣忔棩澶囦唤OpenClaw娴嬭瘯妗嗘灦"
```

## 馃攧 鎭㈠鏂规硶

### 鎯呭喌1锛氶噸鏂板畨瑁匫penClaw鍚?```bash
# 1. 瀹夎OpenClaw鍚庯紝杩愯鎭㈠鑴氭湰
python D:\\OpenClaw_TestingFramework\restore_testing_framework.py

# 2. 杩愯鑷姩鍔犺浇鍣紙鍙€夛級
python D:\\OpenClaw_TestingFramework\auto_load_testing.py
```

### 鎯呭喌2锛氬伐浣滅┖闂存崯鍧?```bash
# 1. 鍒犻櫎鎹熷潖鐨勫伐浣滅┖闂?rmdir /s /q C:\Users\cqs10\.openclaw\workspace

# 2. 閲嶆柊鍒涘缓骞舵仮澶?mkdir C:\Users\cqs10\.openclaw\workspace
python D:\\OpenClaw_TestingFramework\restore_testing_framework.py
```

### 鎯呭喌3锛氫粠浜戝瓨鍌ㄦ仮澶?```bash
# 1. 浠庝簯瀛樺偍涓嬭浇澶囦唤鏂囦欢
# 2. 鏀剧疆鍒板浠界洰褰?# 3. 杩愯鎭㈠鑴氭湰
python D:\\OpenClaw_TestingFramework\restore_testing_framework.py
```

## 馃殌 鏈€浣冲疄璺?
### 1. 澶氫綅缃浠?```yaml
澶囦唤绛栫暐:
  - 涓诲浠? D:\\OpenClaw_TestingFramework\
  - 浜戝浠? OneDrive\OpenClaw_Backups\
  - 鐗堟湰鎺у埗: GitHub浠撳簱
  - 澶栭儴澶囦唤: 姣忔湀澶囦唤鍒癠SB椹卞姩鍣?```

### 2. 瀹氭湡楠岃瘉
```bash
# 姣忔湀楠岃瘉澶囦唤瀹屾暣鎬?python D:\\OpenClaw_TestingFramework\restore_testing_framework.py --verify

# 妫€鏌ユ枃浠跺畬鏁存€?Get-FileHash D:\\OpenClaw_TestingFramework\security_scanner.py
```

### 3. 鐗堟湰绠＄悊
```bash
# 浣跨敤Git杩涜鐗堟湰鎺у埗
cd D:\\OpenClaw_TestingFramework
git init
git add .
git commit -m "娴嬭瘯妗嗘灦 v1.0.0"
git remote add origin https://github.com/yourname/openclaw-testing-framework.git
git push -u origin main
```

### 4. 鏇存柊绛栫暐
```markdown
鏇存柊娴佺▼:
1. 鍦ㄥ伐浣滅┖闂翠慨鏀规祴璇曟鏋?2. 娴嬭瘯淇敼鏁堟灉
3. 澶囦唤鍒板畨鍏ㄤ綅缃?4. 鎻愪氦鍒扮増鏈帶鍒?5. 鎺ㄩ€佸埌浜戝瓨鍌?```

## 馃搵 妫€鏌ユ竻鍗?
### 澶囦唤妫€鏌ユ竻鍗曪紙姣忔湀锛夛細
- [ ] 涓诲浠界洰褰曞瓨鍦ㄤ笖鍙闂?- [ ] 鎵€鏈夋枃浠跺畬鏁达紙鏃犳崯鍧忥級
- [ ] 鎭㈠鑴氭湰鍙甯歌繍琛?- [ ] 浜戝浠藉悓姝ユ甯?- [ ] 鐗堟湰鎺у埗鎻愪氦鏈€鏂?- [ ] 澶栭儴澶囦唤鏇存柊

### 鎭㈠妫€鏌ユ竻鍗曪紙閲嶆柊瀹夎鍚庯級锛?- [ ] OpenClaw瀹夎瀹屾垚
- [ ] 宸ヤ綔绌洪棿鐩綍瀛樺湪
- [ ] 鎭㈠鑴氭湰杩愯鎴愬姛
- [ ] 娴嬭瘯妗嗘灦鏂囦欢瀹屾暣
- [ ] 瀹夊叏妫€鏌ヨ剼鏈彲杩愯
- [ ] 鍙戝竷妫€鏌ユ竻鍗曞彲杩愯

## 馃洝锔?绱ф€ユ儏鍐靛鐞?
### 鍦烘櫙1锛氬浠戒涪澶?```markdown
瑙ｅ喅鏂规:
1. 浠庝簯瀛樺偍涓嬭浇鏈€鏂板浠?2. 浠庣増鏈帶鍒舵仮澶?3. 浠庢湰鏂囨。閲嶆柊鍒涘缓
4. 鑱旂郴鑾峰彇甯姪
```

### 鍦烘櫙2锛氭仮澶嶅け璐?```markdown
瑙ｅ喅鏂规:
1. 妫€鏌ラ敊璇俊鎭?2. 鎵嬪姩澶嶅埗鏂囦欢
3. 楠岃瘉鏂囦欢鏉冮檺
4. 妫€鏌ython鐜
```

### 鍦烘櫙3锛氭枃浠舵崯鍧?```markdown
瑙ｅ喅鏂规:
1. 浠庡叾浠栧浠戒綅缃仮澶?2. 浣跨敤鐗堟湰鎺у埗鍘嗗彶
3. 閲嶆柊涓嬭浇鎴栧垱寤?```

## 馃摓 鏀寔涓庡府鍔?
### 鑾峰彇甯姪锛?1. **鏂囨。**锛氶槄璇绘湰鎸囧崡鍜宍TESTING_FRAMEWORK.md`
2. **鑴氭湰甯姪**锛氳繍琛?`python security_scanner.py --help`
3. **闂鍙嶉**锛氳褰曢棶棰樺苟瀵绘眰瑙ｅ喅鏂规
4. **绀惧尯鏀寔**锛歄penClaw绀惧尯鎴朑itHub Issues

### 鑱旂郴淇℃伅锛?- **澶囦唤浣嶇疆**锛歚D:\\OpenClaw_TestingFramework\`
- **鎭㈠鑴氭湰**锛歚restore_testing_framework.py`
- **鑷姩鍔犺浇**锛歚auto_load_testing.py`
- **鏂囨。**锛歚BACKUP_AND_RESTORE_GUIDE.md`

## 馃幆 鎬荤粨

### 鍏抽敭瑕佺偣锛?1. **宸ヤ綔绌洪棿涓嶆槸姘镐箙瀛樺偍** - 蹇呴』澶囦唤鍒板畨鍏ㄤ綅缃?2. **澶氫綅缃浠?* - 闃叉鍗曠偣鏁呴殰
3. **瀹氭湡楠岃瘉** - 纭繚澶囦唤鍙敤
4. **鑷姩鍖栨仮澶?* - 蹇€熸仮澶嶆祴璇曟鏋?
### 琛屽姩椤圭洰锛?1. 鉁?**绔嬪嵆澶囦唤**锛氬鍒舵枃浠跺埌瀹夊叏浣嶇疆
2. 鉁?**鍒涘缓鎭㈠鑴氭湰**锛氳嚜鍔ㄥ寲鎭㈠杩囩▼
3. 鉁?**璁剧疆鑷姩鍔犺浇**锛氭瘡娆′細璇濊嚜鍔ㄥ姞杞芥鏋?4. 馃攧 **瀹氭湡缁存姢**锛氭瘡鏈堟鏌ュ浠藉畬鏁存€?
### 鏈€缁堢洰鏍囷細
**纭繚娴嬭瘯鍜屽畨鍏ㄦ鏋跺湪浠讳綍鎯呭喌涓嬮兘鍙敤锛屽嵆浣块噸鏂板畨瑁匫penClaw锛?*

---

**澶囦唤涓嶆槸鍙€夐」锛屾槸蹇呴』椤广€?*  
**瀹夊叏娴嬭瘯妗嗘灦鏄疂璐佃祫浜э紝鍔″繀濡ュ杽淇濇姢锛?*

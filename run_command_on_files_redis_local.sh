#!/bin/bash

# 獲取昨天的日期
yesterday=$(date -d "yesterday" +%Y-%m-%d)

# 文件名模式
filename_pattern="automatic.redis-db-002"

# 目錄位置，根據您的需求修改
directory="/tmp"

# 在指定目錄中尋找符合條件的文件
# -maxdepth 1 使搜索不會進入子文件夾
for file in $(find $directory -maxdepth 1 -type f -name "$filename_pattern*-$yesterday-*.rdb"); do
  echo "Processing $file"
  # 執行您想要的命令 並過濾特定的大key 
  /usr/local/bin/rdb -c protocol --db 1 --not-key '^core_user_token_list$|^core_charm_fans_count:$|^core_charm_follow_count:$|^core_game_tbtguil$' "$file"  | redis-cli -p 6380 -n 1 --pipe
done






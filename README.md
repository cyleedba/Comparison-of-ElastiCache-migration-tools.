# AWS-elasticache migration 

aws elasticache 有限制一些指令的使用，想做跨雲的異地同步上限制較多，沒辦法使用 slaveof 或是psync 的方式來達成migration。

https://docs.aws.amazon.com/zh_tw/AmazonElastiCache/latest/red-ug/RestrictedCommands.html


1.

使用 RedisShake 工具來達成異地的同步  [https://github.com/stickermule/rump](https://github.com/tair-opensource/RedisShake)

RedisShake 是阿里雲所開發的開源工具 有支援 sync / restore / scan 三種資料同步的方式

SCAN 非阻塞式的獲取keys 能避免lock的問題

但SCAN 和DUMP 指令會對佔用soure redis instance 較多的CPU 資源。

![image](https://github.com/lkk147852/redis-migration-tool/assets/23359795/facc6959-b74a-4028-8e68-4048451a649c)

RedisShake使用v3 版本時，有使用lua script 把大key給過濾掉，但v3 相對v4 執行時所使用的多執行緒會短時間上升很多 造成 cmds 與new connection 上升太快。

![image](https://github.com/lkk147852/redis-migration-tool/assets/23359795/e70e1987-0c14-4617-9337-4aea132e0b3b)

![image](https://github.com/lkk147852/redis-migration-tool/assets/23359795/18da31b5-a2ad-4a2d-af08-09e84be5b792)

導致後面新的connection 連不進來，前台報503.504 的錯誤。

v4 版本相對v3 在執行時，不會有command 與 new connection 衝太高的問題，但有遇到另一個問題是記憶體使用量太多導致OOM，腳本就直接kill 了。

要migration 到本地的redis 使用 13.x GB ， 預計要抓快30GB ram 才夠

![image](https://github.com/lkk147852/redis-migration-tool/assets/23359795/db08ab2f-2614-48b0-849f-a76a168acb64)  

![image](https://github.com/lkk147852/redis-migration-tool/assets/23359795/d37f41cf-b9b5-4823-9949-da3a0960af4d)

2.

提aws support 工單請他們協助開啟psync 的功能，但會需要對同步的參數做調優。

repl-backlog-size 

repl-backlog-ttl

min-replicas-to-write 和 min-replicas-max-lag

repl-timeout


![image](https://github.com/lkk147852/redis-migration-tool/assets/23359795/92cdaab3-5f79-478c-8912-93847286932a)


3. 
使用 rdb-tool 工具來還原每日備份的rdb檔案 https://github.com/sripathikrishnan/redis-rdb-tools

執行上不影響source redis instance 的資源。


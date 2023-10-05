# AWS-elasticache migration 

aws elasticache 有限制一些指令的使用，想做跨雲的異地同步上限制較多，沒辦法使用 slaveof 或是psync 的方式來達成migration。

![image](https://github.com/lkk147852/redis-migration-tool/assets/23359795/83d92eb8-9cec-4733-8c4c-beedf1866765)


1.

使用 RedisShake 工具來達成異地的同步  [https://github.com/stickermule/rump](https://github.com/tair-opensource/RedisShake)

RedisShake 是阿里雲所開發的開源工具 有支援 sync / restore / scan 三種資料同步的方式

SCAN 非阻塞式的獲取keys 能避免lock的問題

但SCAN 和DUMP 指令會對佔用soure redis instance 較多的CPU 資源。

![image](https://github.com/lkk147852/redis-migration-tool/assets/23359795/facc6959-b74a-4028-8e68-4048451a649c)


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


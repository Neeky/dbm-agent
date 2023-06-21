[toc]

## 克隆插件备份
1. MySQL 数据库备份，目前还只支持 8.0.x + clone 的组合。
   ```bash
   curl  --request POST --header "Content-type:application/json;charset=utf-8" --data '{"backup-type":"clone"}' http://127.0.0.1:8086/apis/mysqls/3306/backup 2>/dev/null | jq
   
   {
     "message": "submit backup mysql using clone task to backends threads.",
     "error": null,
     "data": null
   }
   ```
2. 检查
   ```bash
   tree /database/mysql/backup/3306

   /database/mysql/backup/3306
   └── clone-backup-2023-04-11T23-34-31-842040
       ├── #clone
       │   ├── #replace_files
       │   ├── #status_fix
       │   ├── #view_progress
       │   └── #view_status
       ├── ib_buffer_pool
       ├── ibdata1
       ├── #innodb_redo
       │   └── #ib_redo0
       ├── mysql
       ├── mysql.ibd
       ├── sys
       │   └── sys_config.ibd
       ├── undo_001
       └── undo_002
   
   5 directories, 11 files
   ```

---

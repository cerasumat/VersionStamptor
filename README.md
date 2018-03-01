# 静态文件路径自动添加及文件标记

目录结构
==
##### 功能包含2个文件，分别是：
* 可执行脚本文件：`JsVersioning.py`
* 配置信息文件：`VersionCfg.json`

* * *

##### 执行过程可能生成3个文件，分别是：
* 文件标记信息列表： `VersionMap.json`
* 文件标记结果日志： `replace_log_xxxxxx.log`
* 错误信息日志：`replace_error_log_xxxxxx.log`

* * *

使用方式
==
##### 配置参数
* `root`: 静态资源根目录，默认值：`website` 
* `edition`: 静态资源整体版本号，默认值：`v1` 
* `prefix`: 静态资源服务器路径，将作为静态文件资源前缀被标注，留空则为不替换；默认值：`http://static.chanjet.com`
* `suffix`: 静态资源类型，以`;`分隔，支持多种静态资源标注，默认值：`js;css;png;jpg`
* `srcpath`: 需要替换的html页面路径，绝对路径，留空则取脚本文件当前目录；
* `dstpath`: 静态资源路径，绝对路径，留空则与`srcpath`一致；  
* `stamptype`: 静态资源标记类型，`hash`为散列值标注，`time`为时间标记；默认值：`hash`  
* `forced`: 是否替换无`?t=`标记的静态资源内容；默认值：`true`
* `detailed`： 替换过程是否输出控制台信息；默认值：`true`
* `logged`： 是否生成替换结果日志信息；默认值:`true`

* * *

##### 使用方法
* 修改确认配置参数
* 使用python3.x直接执行脚本文件即可；
* 可在执行命令行中动态输入参数，将覆盖配置文件中的参数，可通过`help()`查看帮助信息；  


* * *

##### 脚本下载
* 各日期版本下载文件见回复内容

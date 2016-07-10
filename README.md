# dalmatian -- 斑点狗

一个爬虫系统，捉去豆瓣电影,用于数据分析，然后会通过推荐系统推送给用户

开发环境：

- 数据库：mysql
- 爬虫框架：scrapy
- 系统：mac osx

## douban_movie

使用需要修改`douban_movie/douban_movie/settings.py`文件夹里面的数据库配置：host, port, username, password

在`douban_movie`目录下面，跑命令：

```python
scrapy crawl douban_movie
```
# Ajax爬取头条街拍美图

## url： https://www.toutiao.com/search/?keyword=街拍
### 抓取分析：
* 打开第一个网络请求，url为当前链接，preview查看Response body，没有，再直接看Response，尝试搜索单个结果的标题，如“3A街拍”
    发现源代码没有包含，判断内容由Ajax加载，再用JS渲染，切换到XHR，看Ajax请求
* 点开data字段，第一条，有个title字段，值就是标题，其他数据一一对应。具体每条数据，都有个image_list字段，包含组图图片列表
* 查看Headers选项卡，GET请求，URL参数有offset format keyword autoload count cur_tab 比较规律，只有offset改变

### 步骤 还是请求、爬取、保存
#### 两种方式，第一种最简洁
1. test.py，直接在原页面做所有事情，注意：**需要加工image的信息，小图变大图**
2. spider.py 打开新的链接，再爬取大图所在页
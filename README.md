# CVE-2021-3129
Laravel debug rce

# 食用方法
执行`docker-compse up -d`启动环境

访问`8888`端口后点击首页面的`generate key`就可以复现了  

关于docker环境想说的几点：
- 把.env.example复制到.env作用是开启debug环境
- 关闭了php.ini的phar.readonly
- 在resources/view/里添加了一个hello模板并引用了一个未定义变量，同时在routes/web.php添加路由(这个我加在源码里了，没写dockerfile里)  

# 复现效果 

![复现效果](https://raw.githubusercontent.com/SNCKER/CVE-2021-3129/master/pic/1.jpg)

脚本已放出，脚本要和phpggc项目文件夹在同一级目录下。  
通用性不强（至少打我自己的环境可以），大家可自行把phpggc的其它rce链也加进去，提高通杀能力。  

# 参考资源
https://www.ambionics.io/blog/laravel-debug-rce  
https://xz.aliyun.com/t/9030#toc-3  
https://blog.csdn.net/csdn_Pade/article/details/112974809  

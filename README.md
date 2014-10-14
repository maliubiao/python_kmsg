python-kmsg
===========

###用于读取/dev/kmsg工具
假设你载入了下面的内核模块，为了获取输出信息，得读取/dev/kmsg
```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h> 

MODULE_LICENSE("Dual BSD/GPL");

MODULE_AUTHOR("user <user@mail.com>");

static int __init hello_init(void)
{
	printk(KERN_ALERT "Hello World\n");
	return 0;
}

static void __exit hello_exit(void)
{
	printk(KERN_ALERT "Goodbye, cruel world\n");
} 

module_init(hello_init);
module_exit(hello_exit);
``` 
###用这个工具过滤
```shell
python kmsg.py -p alert
[{ 
'fac': 0,
'msg': 'Hello World',
'other': '-',
'pri': 1,
'seqnum': 405,
'tags': None,
'timestamp': 3244422641},
{
'fac': 0,
'msg': 'Goodbye, cruel world',
'other': '-',
'pri': 1,
'seqnum': 406,
'tags': None,
 'timestamp': 3254023037 
}] 
```
##选项有 
-p 根据优先级，分别为emerg, alert, crit, err, warn, notice, info, debug
-f 根据类别, 分别为kernel, user, mail, daemon, auth, syslog, lpr, news, uucp, cron, authpriv, ftp 

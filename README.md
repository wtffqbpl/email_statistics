# email_statistics
Check your email and send results to your specified email.

#### 使用方式：
        1. 将上述压缩包上传到服务器，解压后进入该目录。
        2. 修改配置文件(.configuration.cfg)中的相关参数。具体参数见附表。
        3. 执行python check_work_time.py 命令即可完成加班时间统计的任务，同时会发送邮件到配置的邮箱中。
        4. Enjoy!


#### 附录A: 配置文件中的参数详解

<table>
    <tr>
        <td>一级参数</td> 
        <td>二级参数</td> 
        <td>参数含义</td> 
   </tr>
   <tr>
        <td rowspan="7">mailaccountinfo</td> 
        <td>imaphostname</td> 
        <td> 发送每日工作邮箱的imap服务器地址。其中，平时使用的两个邮箱imap地址如下所示 腾讯企业邮箱：imap.exmail.qq.com阿里企业邮箱：imap.mxhichina.com
</td> 
   </tr>
   <tr>
        <td>imapusername</td> 
        <td>发送每日工作报告的邮箱用户名。</td> 
   </tr>
   <tr>
        <td>imappassword</td> 
        <td>发送每日工作报告的邮箱密码。</td> 
   </tr>
   <tr>
        <td>smtphostname</td> 
        <td>采用哪个邮箱将查询的结果发送到指定邮箱中。这里配置所采用邮箱的smtp服务器地址。平时使用的两个邮箱smtp地址如下：腾讯企业邮箱：smtp.exmail.qq.com阿里企业邮箱：smtp.mxhichina.com</td> 
   </tr>
   <tr>
        <td>Smtphostname</td> 
        <td>发送邮件的邮箱用户名。</td> 
   </tr>
   <tr>
        <td>smtppassword</td> 
        <td>发送每日工作报告的邮箱用户名。</td> 
   </tr>
   <tr>
        <td>imapusername</td> 
        <td>发送邮件的邮箱密码。</td> 
   </tr>
   <tr>
        <td>Mailfolder</td> 
        <td>需要在哪个邮箱目录中查找。注：1）如果需要查询自己的每日工作邮件，请配置SENT目录即可，即从发件箱中发送的邮件中进行统计。2）如果需要统计其他同事的时间，可将该目录配置为INBOX，即从收件箱中接收到的邮件来进行统计。</td> 
   </tr>
   <tr>
        <td>employees</td>    
        <td >namelist</td>  
        <td>需要查询的用户列表。这里请配置发件人的邮箱地址，其中多个邮箱用逗号隔开。</td> 
   </tr>
   <tr>
        <td>mailtolist</td>    
        <td >namelist</td>  
        <td>查询得到的结果需要发送给哪些邮箱，如需发送到多个邮箱，邮箱之间请用逗号隔开。</td> 
   </tr>
   <tr>
        <td rowspan="4">time</td>  
        <td >time1</td>  
        <td >第一阶段的加班时间（这里配置19:30:00）</td>  
   </tr>
   <tr>
        <td >time2</td>  
        <td >第二阶段的加班时间（这里配置21:00:00）</td>  
   </tr>
   <tr>
        <td >day_start</td>  
        <td >统计开始的日期（包含该天）</td>  
   </tr>
   <tr>
        <td >day_end</td>  
        <td >计结束的日期（统计时不包含该天）。</td>  
   </tr>
   <tr>
        <td >sendmail</td>  
        <td >sendmail</td>  
        <td >是否需要发送邮件到指定邮箱中，如果是，请填写True，反之填写False</td>  
   </tr>
</table>
	
Enjoy!

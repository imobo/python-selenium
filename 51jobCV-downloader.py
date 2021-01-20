import os
import datetime
import time

from selenium  import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException


def create_proxyauth_extension(proxy_host, proxy_port,
                               proxy_username, proxy_password,
                               scheme='http', plugin_path=None):
    """Proxy Auth Extension

    args:
        proxy_host (str): domain or ip address, ie proxy.domain.com
        proxy_port (int): port
        proxy_username (str): auth username
        proxy_password (str): auth password
    kwargs:
        scheme (str): proxy scheme, default http
        plugin_path (str): absolute path of the extension       

    return str -> plugin_path
    """
    import string
    import zipfile

    if plugin_path is None:
        plugin_path = 'vimm_chrome_proxyauth_plugin.zip'

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = string.Template(
    """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "${scheme}",
                host: "${host}",
                port: parseInt(${port})
              },
              bypassList: ["foobar.com"]
            }
          };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "${username}",
                password: "${password}"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """
    ).substitute(
        host=proxy_host,
        port=proxy_port,
        username=proxy_username,
        password=proxy_password,
        scheme=scheme,
    )
    with zipfile.ZipFile(plugin_path, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return plugin_path



#文件、环境变量设置
p = os.path.abspath(__file__)
d = os.path.dirname(p)
chromedriver= d + r"\chromedriver.exe"

os.environ["webdriver.chrome.driver"] = chromedriver


#端口设置

proxyauthPluginPath = create_proxyauth_extension(
            proxy_host='10.249.177.131',
            proxy_port='8080',
            proxy_username="internet",
            proxy_password="CHAMInterneT")


#webdriver设置
options = webdriver.ChromeOptions()
options.add_extension(proxyauthPluginPath)

driver = webdriver.Chrome(executable_path=chromedriver,chrome_options=options)
driver.maximize_window()



def login():
    driver.get(r"https://ehire.51job.com/")
    time.sleep(3)
    
    #账户密码
    cnIdInputElement = driver.find_element_by_name("txtMemberNameCN")
    cnIdInputElement.clear()
    cnIdInputElement.send_keys("name1")

    idInputElement = driver.find_element_by_name("txtUserNameCN")
    idInputElement.clear()
    idInputElement.send_keys("name2")
    
    pwInputElement = driver.find_element_by_name("txtPasswordCN")
    pwInputElement.clear()
    pwInputElement.send_keys("pw")

    #点击登录
    driver.find_element_by_css_selector("[class='btn-blue-g']").click()
    time.sleep(3)



def setFilterStaff(post,sex=None):
    driver.get(r"https://ehire.51job.com/InboxResume/InboxRecentEngine.aspx?Style=1")

    #展开条件
    elem = driver.find_element_by_xpath('//a[@class="controlSet"]')
    elem.click()
    #选择学历
    try:
        elem = driver.find_element_by_id('ctlSearchInboxEngine1_txt_degreefrom')
        driver.execute_script("arguments[0].click();",elem)
        elem = driver.find_element_by_id('dic_degreefrom_5')
        driver.execute_script("arguments[0].click();",elem)
    except Exception:
        pass
        
    #选择性别
    try:
        if sex != None:        
            elem = driver.find_element_by_id('ctlSearchInboxEngine1_txt_sex')
            driver.execute_script("arguments[0].click();",elem)
            if sex == "男":
                elem = driver.find_element_by_id('dic_sex_0')
            elif sex == "女":
                elem = driver.find_element_by_id('dic_sex_1')
            driver.execute_script("arguments[0].click();",elem)
    except Exception:
        pass
        
    #选择期望工资
    try:
        elem = driver.find_element_by_id('ctlSearchInboxEngine1_txt_expectsalaryto')
        driver.execute_script("arguments[0].click();",elem)
        elem = driver.find_element_by_id('dic_expectsalaryto_08')
        driver.execute_script("arguments[0].click();",elem)
    except Exception:
        pass
        
    #输入职位 - 根据参数
    try:
        elem = driver.find_element_by_id("ctlSearchInboxEngine1_txt_positionapplied")
        elem.clear()
        elem.send_keys(post)
    except Exception:
        pass
    #搜索
    elem = driver.find_element_by_xpath('//a[@class="btn-search"]')
    elem.click()   



def checkDownloadResume():
    
    #读取历史记录txt
    import os
    path = r"E:\\"
    txtName = "#CVcheck(51).txt"

    p = path + "\\" + txtName
    file = open(p,"r+")
    d = []
    for l in file:
        d.append(l)


    #确认页面数据(项数)
    temp1 = driver.find_element_by_id("labAllResumes").text
    temp2 = temp1[1:]                                               #去掉 “共”
    allResumes = int(temp2[:-1])                                    #去掉 “页”
    if allResumes<50:
        rowNum = allResumes + 1
    else:
        rowNum = 51


    #取得页面数据（50项）
    flag = 0
    for i in range(1,rowNum):
        s = "trBaseInfo_" + str(i)
        try: 
            name = driver.find_element_by_id(s).find_element_by_class_name('a_username').text
            post = driver.find_element_by_id(s).find_elements_by_tag_name("td")[3].text
            age = driver.find_element_by_id(s).find_elements_by_tag_name("td")[6].text
            degree = driver.find_element_by_id(s).find_elements_by_tag_name("td")[7].text
            major = driver.find_element_by_id(s).find_elements_by_tag_name("td")[8].text
            infrom = name + post + age + degree + major + "\n"
        except NoSuchElementException:
            print("element not find. Skipping ",s)
            continue

        #T确认重复值
        if infrom not in d:
            #IF NOT OVERLAPPING, CLICK ON CHECK BOX
            driver.find_element_by_id(s).find_element_by_id('chkBox').click()
            file.write(infrom)
            flag = 1

    if flag == 1:
        file.write("\n")

        #下载简历 - 选择excel格式 - 下载按钮
        js="InboxEngine.OpenResumeCommonLayer('Export')"
        driver.execute_script(js)

        js = driver.find_element_by_xpath(".//input[@type='radio' and @value='Excel']")
        driver.execute_script("arguments[0].click();", js) 

        js="EHRExportBox.Send()"
        driver.execute_script(js)

        
    file.close()
    print("... " + post + " CV check completed")
    



def refreshPost():
    driver.get(r"https://ehire.51job.com/Jobs/JobSearchPost.aspx")
    driver.find_element_by_id('radSelactALLt').click()

    js = driver.find_element_by_id('batch_refresh')
    driver.execute_script("arguments[0].click();", js)

    js = driver.find_element_by_xpath('//a[@class="panel_btn_s ehrui-button"]')
    driver.execute_script("arguments[0].click();", js)

    print("... Post refresh completed")



def strHandler(a,b):
    # a: str to be handle     b: list object to be remove
    # 返回 移除了LIST第一个符合的符号后的字符串
    for s in b:
            result = a.find(s,0,len(a))
            if result >=0:
                    tempStr=[]
                    
                    for temp in range(len(a)):
                            if a[temp] != s:
                                    tempStr.append(a[temp])
                            else:
                                    tempStr.append("")
                                    
                    t = ""
                    for temp in range(len(tempStr)):
                            t=t+tempStr[temp]
                    return t
            else:                                       # a.find(s,0,len(a)) = -1
                return a



def fileRename(post):
    import os
    import time
    
    path = r"C:\\Downloads\\"                                   #下载路径
    files = os.listdir(path)                                    #取得路径中的文件列表
    t = time.strftime("%Y-%m-%d", time.localtime())             #取得现在时间，格式为“2020-07-29”

    for f in files:
        temp = f[:5]                                            #取右5位字符
        if temp=="51job":
            postName = strHandler(post,["/"])                   #REMOVE "/" IN POST NAME,IF ANY
            newName = "51 " + postName + " " + t + " 简历.xls"  #新命名文件名称
            newfile = os.path.join(path,newName)
            oldfile = os.path.join(path,f)
            os.rename(oldfile,newfile)
            print("rename form "+ f + " to " + newName)



# execute script
if __name__ == "__main__":
    
    import time
    start = time.time() #记下开始时刻
    login()                                             #登录    
    refreshPost()                                       #刷新职位

                                                        #post：staff post
    post = ["HR staff"]
    postMale = []
                                                                #staff岗位循环
    for p in post:
        if p in postMale:
            setFilterStaff(p,"男")
        else:
            setFilterStaff(p)
            
        checkDownloadResume()
        time.sleep(5)
        fileRename(p)

    end = time.time()   #记下结束时刻
    print ("all completed.用时",round((end - start)/60,4),"分")

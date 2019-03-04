# -*- coding: utf-8 -*-
import os
import sys
import time
import hashlib
import smtplib
#import requests
#import json

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

# 需要配置分割线 ===================================================================

# 项目配置
project_name    = "Coin"         # 工程名
scheme          = "Coin"         # scheme
project_type    = "-workspace"        # 工程类型 pod工程 -workspace 普通工程 -project

configuration   = "Release"             # 编译模式 Debug,Release
#configuration   = "Debug"             # 编译模式 Debug,Release

project_path    = "~/Desktop/工作/CoinJob/二期/Coin"         # 项目根目录
pack_robot_path = "~/Desktop/PackRobot"                        # 打包后ipa存储目录 请指向自动打包脚本所在目录
ERCodeImage_path = "~/Desktop/PackRobot/ERCode.png"              # 下载地址的二维码路径

# 092425b3-ea29-4931-8670-68d2d6f4cd54 pru
# 3a2c483b-d35d-42d0-a68d-7acc0388fc86 dev
#mobileprovision_uuid = "092425b3-ea29-4931-8670-68d2d6f4cd54"    # mobileprovision uuid,不能使用 xcode 自动生成的文件,需要为手动管理的配置文件

mobileprovision_uuid = "07d9f79b-dd02-46f4-bf28-fd2f9cdec00f"    # mobileprovision uuid,不能使用 xcode 自动生成的文件,需要为手动管理的配置文件


#signing_certificate =  "iPhone Distribution: Calazova International Co.,Ltd. (9WEX89NG79)"
signing_certificate = "iPhone Distribution: Calazova International Co.,Ltd. (9WEX89NG79)"      # 证书名称

# fir 如果不使用,请不要修改此处.
fir_api_token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # firm的api token
download_address = "https://fir.im/xxxxxxxxx"   # firm 下载地址

# pgyer
pgyer_uKey         = "9f7d4257c69b087cae4a42dc8639a331"
pgyer_apiKey       = "78f497500747a34068cf2985c8e26340"
pgyer_appQRCodeURL = "https://www.pgyer.com/kismart_beta"   # 下载地址
pgyer_installType  = 1                                  # 1：公开，2：密码安装，3：邀请安装。
pgyer_password     = "12345"
pgyer_updateDescription = "version 1.4.1"                     # 更新描述

# 邮件配置
#app_name = "阿里邮箱企业版"   #App名
#from_name = "lvyongtao" #对方显示的账户名称
#from_addr = "" #账号
#password = ""  #密码
#smtp_server = "smtp.mxhichina.com" #smtp 服务
#to_addr = ['liule@kismart.com.cn']

# 需要配置分割线 ===================================================================

# 清理项目
def clean_project():
    print("** PACKROBOT START **")
    os.system('cd %s;xcodebuild clean' % project_path) # clean 项目

# archive项目
def build_project():
    os.system('cd %s;mkdir build' % project_path)
    if project_type == "-workspace" :
        project_suffix_name = "xcworkspace"
    else :
        project_suffix_name = "xcodeproj"
    os.system ('cd %s;xcodebuild archive %s %s.%s -scheme %s -configuration %s -archivePath %s/build/%s CODE_SIGN_IDENTITY="%s" PROVISIONING_PROFILE="%s" || exit' % (project_path,project_type,project_name,project_suffix_name,scheme,configuration,project_path,project_name,signing_certificate,mobileprovision_uuid))

# 导出ipa包到自动打包程序所在目录
def exportArchive_ipa():
    global ipa_filename
    ipa_filename = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
    ipa_filename = project_name + "_" + ipa_filename;
    os.system ('%s/xcodebuild-safe.sh -exportArchive -archivePath %s/build/%s.xcarchive -exportPath %s/%s -exportOptionsPlist %s/exportOptionsPlist.plist ' %(pack_robot_path,project_path,project_name,pack_robot_path,ipa_filename,pack_robot_path))

# 删除build目录
def rm_project_build():
    os.system('rm -r %s/build' % project_path)

# 上传
def upload_app():
    local_path_filename = os.path.expanduser(pack_robot_path)  # 相对路径转换绝对路径
    
    if os.path.exists("%s/%s" % (local_path_filename,ipa_filename)):
        if (fir_api_token == "xxxxxxxxxxxxxxxxxxxxxxxxxxxx"):
            filePath = "%s/%s/%s.ipa" % (local_path_filename,ipa_filename,project_name)
            ret = os.system('curl -F "file=@%s" -F "uKey=%s" -F "_api_key=%s" -F "installType=%s" -F "password=%s" -F "updateDescription=%s" https://www.pgyer.com/apiv2/app/upload' % (filePath, pgyer_uKey, pgyer_apiKey, pgyer_installType, pgyer_password, pgyer_updateDescription))
        # curl -F "file=users/user/desktop/PackRobot/KismartUser_2018-11-08-18-19-02/KismartUser_debug.ipa" -F "uKey=9f7d4257c69b087cae4a42dc8639a331" -F "_api_key=78f497500747a34068cf2985c8e26340" https://www.pgyer.com/apiv2/app/upload
#        print("** pugogying uploading **")

        else:
            # 直接使用fir 有问题 这里使用了绝对地址 在终端通过 which fir 获得
            ret = os.system("fir publish '%s/%s/%s.ipa' --token='%s'" % (pack_robot_path,ipa_filename,project_name,fir_api_token))
    else:
        print("没有找到ipa文件")

# 地址格式化
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

# 发邮件
def send_mail():
    msgRoot = MIMEMultipart('related')
    msgRoot['From'] = _format_addr('%s''<%s>' % (from_name,from_addr))
    msgRoot['To'] = ",".join(_format_addr('%s' % to_addr))
    msgRoot['Subject'] = Header(app_name + " iOS 客户端版本构建完成, 构建时间:" + time.strftime('%Y年%m月%d日%H:%M:%S',time.localtime(time.time())), 'utf-8').encode()
    if (fir_api_token == "xxxxxxxxxxxxxxxxxxxxxxxxxxxx"):
        msgText = MIMEText(app_name + " iOS客户端已经打包完毕，请扫描附件中的二维码或前往 " + pgyer_appQRCodeURL + " 下载测试！", 'plain', 'utf-8')
    else:
        msgText = MIMEText(app_name + " iOS客户端已经打包完毕，请扫描附件中的二维码或前往 " + download_address + " 下载测试！", 'plain', 'utf-8')
    msgRoot.attach(msgText)

    # 添加图片类型附件
    local_path_filename = os.path.expanduser(ERCodeImage_path)
    if(os.path.exists(local_path_filename)) :
        fpath,fname = os.path.split(local_path_filename)
        with open(local_path_filename, 'rb') as imageFile:
            mime = MIMEBase('image', 'png', filename = fname)
            mime.add_header('Content-Disposition', 'attachment', filename=fname)
            mime.add_header('Content-ID', '<0>')
            mime.add_header('X-Attachment-Id', '0')
            mime.set_payload(imageFile.read())
            encoders.encode_base64(mime)
            msgRoot.attach(mime)

    server = smtplib.SMTP(smtp_server, 465)
    server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr,to_addr, msgRoot.as_string())
    server.quit()

# 输出包信息
def ipa_info():
    print '\n'
    local_path_filename = os.path.expanduser(pack_robot_path)  # 相对路径转换绝对路径
    print "ipa file location information --- %s/%s/%s.ipa" % (local_path_filename,ipa_filename,project_name)
    print '\n'
    
    print("** PACKROBOT SUCCEEDED **")

def main():
    # 清理并创建build目录
    clean_project()
    # 编译目录
    build_project()
    # 导出ipa到机器人所在目录
    exportArchive_ipa()
    # 删除build目录
    rm_project_build()
    # 上传
    upload_app()
    # 发邮件
#    send_mail()
    #输出包信息
    ipa_info()

# 执行
main()

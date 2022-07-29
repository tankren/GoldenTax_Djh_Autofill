from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename
from lxml import etree
#importing other modules
import logging, os, sys, subprocess, time, datetime
os.popen("chcp 936")

start=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
logfile='处理日志_' + start + '.txt'


for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
#now we will Create and configure logger 
logging.basicConfig(filename='处理日志.txt', 
					format='%(asctime)s - %(levelname)s: %(message)s', 
					filemode='w',
                    encoding='utf-8', 
                    level=logging.DEBUG) 

#Let us Create an object 
logger=logging.getLogger() 

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing

xmlfile = askopenfilename(filetypes=[('XML文件', '.xml')],title='选择金税系统导出XML文件') # show an "Open" dialog box and return the path to the selected file
txtfile = askopenfilename(filetypes=[('TXT文件', '.txt')],title='选择批量导入结果TXT文件')
print('XML文件为:',xmlfile)
print('TXT文件为:',txtfile)    
logger.info(f'选择的XML文件为: {xmlfile}')
logger.info(f'选择的TXT文件为: {txtfile}')

if xmlfile == '' or txtfile == '':
    print('文件选择有误,程序将退出,请重新运行')
    logger.warning('文件选择有误,程序将退出,请重新运行')
    logging.shutdown()
    os.rename('处理日志.txt', logfile)
    subprocess.Popen(['notepad.exe', logfile])
else:    
    xml = etree.parse(xmlfile) #读取xml文件
    root = xml.getroot() #获取根节点
    
    for fphm in root.xpath('//Fphm'):
        print('发票号码为:',fphm.text)
        logger.info(f'发票号码为: {fphm.text}')
        for ancestor in fphm.iterancestors('Fp'):
            djh=ancestor.find('./Djh')
            #Lbdm=ancestor.find('./Lbdm').text
            print('对应的原始单据号是:',djh.text)
            logger.info(f'对应的原始单据号是:{djh.text}')
            #print('对应的lbdm是:',Lbdm)
            print('开始查找对应的单据号...')
            logger.info('开始查找对应的单据号...')
            with open(txtfile,"r",encoding="gb2312") as mapping:
                data = mapping.readlines()    
                for line in data:
                    if fphm.text in line:
                        import re
                        pattern = re.compile(r"\d{10}")
                        map = pattern.findall(line)[0]
                        if map == '':
                            print('发票号码',fphm.text,'未匹配到单据号')
                            logger.info(f'发票号码{fphm.text}未匹配到单据号')
                        else:
                            print('匹配到的单据号为:',map,'修改XML单据号...')
                            logger.info(f'匹配到的单据号为: {map} 修改XML单据号...')
                            djh.text = map
                            #newxml=xmlfile+'_new.xml'
                            xml.write(xmlfile,pretty_print=True)
                            print('修改成功!!')
                            logger.info('修改成功!!')
    logging.shutdown()
    os.rename('处理日志.txt', logfile)
    subprocess.Popen(['notepad.exe', logfile])
    subprocess.Popen(['C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',xmlfile])
    time.sleep(5)
    sys.exit()
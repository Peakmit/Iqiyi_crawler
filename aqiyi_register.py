import logging
import random
import time

from selenium import webdriver

from MSG_Finder import Robot, Collect_Message

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class Iqiyi(object):
    """
    自动实现注册，验证码接受，滑块验证码的实现
    """

    def __init__(self, phone_num):
        self.web_driver = webdriver.Chrome()
        self.web_driver.maximize_window()
        self.web_driver.implicitly_wait(10)
        self.nation, self.phone_num = phone_num.split()
        self.url = 'https://www.iqiyi.com/'

    def input_phone_num(self):
        """
        根据国家区号进行输入手机号码
        """
        # 更换地区
        time.sleep(1)
        self.web_driver.find_element_by_xpath(
            '/html/body/div[2]/div/div[2]/div[1]/div[1]/div[1]/div/div[1]/div[1]/span').click()
        self.web_driver.find_element_by_xpath(
            r'/html/body/div[2]/div/div[2]/div[1]/div[1]/div[1]/div/div[1]/div[1]/div/ul/li/a[@data-key="%s"]' %
            self.nation).click()
        # 输入手机号
        time.sleep(1)
        input_box = self.web_driver.find_element_by_xpath(
            '/html/body/div[2]/div/div[2]/div[1]/div[1]/div[1]/div/div[1]/div[2]/input')
        input_box.send_keys(self.phone_num)
        time.sleep(1)
        # 点击下一步
        next_step = self.web_driver.find_element_by_xpath(
            "/html/body/div[2]/div/div[2]/div[1]/div[1]/div[1]/div/a[2]")
        next_step.click()
        logging.info("Successfully input phone_num:%s" % self.phone_num)

    def choose_register(self):
        time.sleep(3)
        # 找到右上角的图像，点击进入登录界面
        login = self.web_driver.find_element_by_id('J-user-wrap')
        login.click()
        self.web_driver.switch_to.frame('login_frame')
        # 点击左下角的注册进入注册界面
        register = self.web_driver.find_element_by_link_text('注册')
        register.click()
        logging.info("Successfully choose register!")

    def message_check_code(self):
        check_code = self.web_driver.find_element_by_xpath(
            '/html/body/div[2]/div/div[2]/div[1]/div[3]/div[1]/div/div[1]/div[2]/div/input')
        # 实现自动爬取手机验证码
        message_collector = Collect_Message(self.nation + self.phone_num)
        code_input = message_collector.run()
        time.sleep(1)
        if code_input is None:
            self.web_driver.quit()
            return
        check_code.send_keys(code_input)
        time.sleep(1)
        self.web_driver.find_element_by_link_text('验证').click()
        logging.info("The check_code:%s\n Suceesfully regester!" % code_input)
        time.sleep(1)

    def run(self):
        self.web_driver.get(url=self.url)
        # 打开登录，选择登录方式为注册
        self.choose_register()
        time.sleep(1)
        # 输入电话号码进入下一步
        self.input_phone_num()
        time.sleep(1)
        # 尝试同意用户协定（第一次注册会有同意用户协定，如果用户已经注册会直接跳过这一步。注册相当于登录过程）
        try:
            check_agreement = self.web_driver.find_element_by_xpath(
                '/html/body/div[2]/div/div[2]/div[1]/div[2]/div[2]/a[2]')
            check_agreement.click()
            time.sleep(1)
        except Exception as ex_results:
            logging.info(" - agreement - Exception:%s" % ex_results)
        # 应对同一个手机号码短信发送太频繁，重启spyder -- 注册限制1
        try:
            check_agreement = self.web_driver.find_element_by_xpath(
                '/html/body/div[2]/div/div[1]/div/div[7]/div/div/a[2]').click()
            self.web_driver.quit()
            logging.info("Rerun the spyder.")
            return
        except Exception as ex_results:
            logging.info(" - over send message - Exception:%s\n" % ex_results)
        # TODO：实现验证码的自动识别（滑块验证码，字体选择验证码） -- 注册限制2
        try:
            self.web_driver.find_element_by_id('test').click()
            input("请手动完成滑动验证码的完成")
        except Exception as excp:
            logging.info(" - Slide Check Code - EXCEPTION：%s" % excp)
        # 输入短信验证码进行验证
        self.message_check_code()
        # 注册成功，退出浏览器
        self.web_driver.quit()


if __name__ == "__main__":
    check_update = input("是否更新手机号码？是，请输入y")
    if check_update == 'y':
        obj = Robot()
        obj.run()
    with open('./source/phone.txt', 'r') as f:
        phones = f.readlines()
        random.shuffle(phones)
        for phone in phones:
            phone = phone.strip('\n')
            Iqiyi_auto_register = Iqiyi(phone)
            Iqiyi_auto_register.run()

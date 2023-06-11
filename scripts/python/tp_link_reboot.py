import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep


def tp_link_reboot():
    """login to and reboot tp link router"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(f'http://{args.ip}')
    driver.implicitly_wait(3)

    username_field = driver.find_element(By.ID, "cloud-login-username")
    username_field.send_keys(args.user)
    sleep(2)

    # password_field = driver.find_element(By.ID, "login-password")
    password_field = driver.find_element(
        By.XPATH, "/html/body/div[1]/div[2]/div[1]/div[1]/div/form[1]/div[2]/div/div/div[1]/span[2]/input[1]")
    password_field.send_keys(args.password)

    login_button = driver.find_element(By.ID, "cloud-login-btn")
    login_button.click()
    sleep(5)

    first_reboot_button = driver.find_element(By.ID, "top-control-reboot")
    first_reboot_button.click()
    sleep(2)

    confirm_button = driver.find_element(By.XPATH, "html/body/div[6]/div[1]/div[4]/div/div/div[2]/div/div[2]/button")
    confirm_button.click()
    exit()


def main():
    tp_link_reboot()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Reboot a tp link router.",
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-i', '--ip', type=str, required=False, default='192.168.1.1', help='Base ip address')
    parser.add_argument('-u', '--user', type=str, required=True, help='Username for logging into router')
    parser.add_argument('-p', '--password', type=str, required=True, help='Password for logging into router')

    args = parser.parse_args()

    main()

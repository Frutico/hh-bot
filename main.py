from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import random
import logging
import requests

def scroll_to_element(driver, element):
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()


def click_element(driver, by, selector):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((by, selector))
        )
        scroll_to_element(driver, element)  # Scroll to the element before clicking
        # Use JavaScript to click at the center of the element, ignoring obscuring elements
        driver.execute_script("arguments[0].click();", element)
        logging.info(f"Successfully clicked on element with selector: {selector}")
    except Exception as e:
        logging.warning(f"Unable to click on element with selector: {selector}. Error: {e}")




def select_resume(resume_name):
    resumes = driver.find_elements(By.CSS_SELECTOR, "span.bloko-radio__text")
    for r in resumes:
        if r.text == resume_name:
            r.click()
            break


def fill_response_letter():
    try:
        click_element(driver, By.CSS_SELECTOR, "button[data-qa='vacancy-response-letter-toggle']")
    except:
        logging.warning("Unable to find toggle button 'response_letter'. Trying to find 'response_letter' textarea.")

    try:
        textarea = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[data-qa='vacancy-response-popup-form-letter-input']"))
        )
        with open('letter.txt') as f:
            letter_text = f.read()
        textarea.send_keys(letter_text)
        logging.info("Textarea 'response_letter' found and filled.")
    except:
        logging.warning("Unable to find 'response_letter' textarea. Skipping response letter.")


def send_resume(resume_name, vacancy_url):
    global today_resume_send
    select_resume(resume_name)

    try:
        click_element(driver, By.CSS_SELECTOR, "button[data-qa='vacancy-response-submit-popup']")
        today_resume_send += 1
        logging.info(f"Job application {vacancy_url} successfully submitted")
        logging.info(f"Resumes have been submitted today: {today_resume_send}")
    except:
        logging.warning("Unable to find send resume button")


def vacancy_have_test(vacancy_id):
    #go to hh api and check
    req = requests.get(f"https://api.hh.ru/vacancies/{vacancy_id}").json()
    has_test = req["has_test"]
    return has_test


def send_resume_for_all_page_vacancies(resume_id):
    vacancies_on_page = driver.find_elements(By.CSS_SELECTOR, "a[data-qa='vacancy-serp__vacancy_response']")
    for vacancy in vacancies_on_page:
        vacancy_url = vacancy.get_attribute('href')
        vacancy_id = vacancy_url.replace('https://spb.hh.ru/applicant/vacancy_response?vacancyId=', '')\
            .replace('&hhtmFrom=vacancy_search_list', '')
        if not vacancy_have_test(vacancy_id):
            vacancy.click()
            time.sleep(random.randint(4, 8))
            send_resume(resume_id, vacancy_url)
        else:
            logging.warning(f"Vacancy {vacancy.get_attribute('href')} has a test. Skipping.")
        time.sleep(random.randint(1, 5))


def authentication():
    with open('login_pass.txt') as f:
        email, password = f.readline().split(":")
    try:
        driver.get("https://spb.hh.ru/account/login")
        driver.find_element(By.CSS_SELECTOR, "button[data-qa='expand-login-by-password']").click()
        username_input = driver.find_element(By.CSS_SELECTOR, "input[data-qa='login-input-username']")
        username_input.send_keys(email)
        password_input = driver.find_element(By.CSS_SELECTOR, "input[data-qa='login-input-password']")
        password_input.send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[data-qa='account-login-submit']").click()
        logging.info(f"Successfully logged in as {email}")
    except:
        logging.error("Can't sign in")


driver = webdriver.Firefox()
today_resume_send = 0


def main():
    global driver
    # setup logging
    logging.basicConfig(level=logging.INFO, filename="hh_log.log", filemode="a"
                        , format="%(asctime)s %(levelname)s %(message)s")

    authentication()
    # wait authentication
    time.sleep(random.randint(4, 10))
    # read resume id
    with open('resume_list.txt', encoding='utf8') as f:
        resumes = f.readlines()

    for resume in resumes:
        resume_id, resume_name = resume.split(":")
        url = f"https://spb.hh.ru/search/vacancy?resume={resume_id}"
        driver.get(url)
        ## send_resume_for_all_page_vacancies(resume_name)
        while driver.find_elements(By.CSS_SELECTOR, "a[data-qa='pager-next']"):
            send_resume_for_all_page_vacancies(resume_name)

    driver.close()


if __name__ == '__main__':
    main()

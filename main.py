from selenium import webdriver
from selenium.webdriver.common.by import By
import time


def select_resume(resume_name):
    resumes = driver.find_elements(By.CSS_SELECTOR, "span.bloko-radio__text")
    for r in resumes:
        if r.text == resume_name:
            r.click()
            break


def fill_response_letter():
    driver.find_element(By.CSS_SELECTOR, "button[data-qa='vacancy-response-letter-toggle']").click()
    textarea = driver.find_element(By.CSS_SELECTOR, "textarea[data-qa='vacancy-response-popup-form-letter-input']")
    letter_text = "text"
    textarea.send_keys(letter_text)


def send_resume(resume_name):
    select_resume(resume_name)
    fill_response_letter()
    driver.find_element(By.CSS_SELECTOR, "button[data-qa='vacancy-response-popup-close-button']").click()
    #driver.find_element(By.CSS_SELECTOR, "button[data-qa='vacancy-response-submit-popup']").click()


def send_resume_for_all_page_vacancies(resume_id):
    vacancies_on_page = driver.find_elements(By.CSS_SELECTOR, "a[data-qa='vacancy-serp__vacancy_response']")
    for vacancy in vacancies_on_page:
        vacancy.click()
        time.sleep(5)
        send_resume(resume_id)
        time.sleep(5)


def authentication():
    with open('login_pass.txt') as f:
        email, password = f.readline().split(":")
    driver.get("https://spb.hh.ru/account/login")
    driver.find_element(By.CSS_SELECTOR, "button[data-qa='expand-login-by-password']").click()
    username_input = driver.find_element(By.CSS_SELECTOR, "input[data-qa='login-input-username']")
    username_input.send_keys(email)
    password_input = driver.find_element(By.CSS_SELECTOR, "input[data-qa='login-input-password']")
    password_input.send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[data-qa='account-login-submit']").click()


driver = webdriver.Firefox()
authentication()
# wait authentication
time.sleep(5)
# read resume id
with open('resume_list.txt', encoding='utf8') as f:
    resumes = f.readlines()

for resume in resumes:
    resume_id, resume_name = resume.split(":")
    url = "https://spb.hh.ru/search/vacancy?resume=" + resume_id
    driver.get(url)
    send_resume_for_all_page_vacancies(resume_name)
    while driver.find_elements(By.CSS_SELECTOR, "a[data-qa='pager-next']"):
        send_resume_for_all_page_vacancies(resume_name)


driver.close()


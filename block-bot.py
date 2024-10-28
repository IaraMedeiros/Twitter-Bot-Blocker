from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
import time

# Configuração inicial
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)
driver.get("https://x.com/i/flow/login")
driver.set_window_size(1024, 600)
driver.maximize_window()
wait = WebDriverWait(driver, 15)

#VARIAVEIS AQUI
username = "yout_username"
email = "your_email"
password = "your_password"
tweet_link = "link to the tweet you want to block bots"

# Função para localizar e clicar em um elemento
def locate_and_click(xpath, wait_time):
    try:
        element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        time.sleep(wait_time)
        element.click()
    except (TimeoutException, StaleElementReferenceException):
        print(f"Erro ao localizar e clicar no elemento com xpath: {xpath}")
        return None

# Função para inserir dados
def insert_data(xpath, data, wait_time=3):
    try:
        element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        time.sleep(wait_time)
        element.clear()
        element.send_keys(data)
        element.send_keys(Keys.ENTER)
    except StaleElementReferenceException:
        print("Elemento obsoleto, tentando localizar novamente...")
        insert_data(xpath, data, wait_time)

# Função para verificar se um elemento existe
def element_exists(xpath):
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        return True  
    except TimeoutException:
        return False 

# LOGIN
try:
    time.sleep(1)
    locate_and_click("//input", 2)
    insert_data("//input", email)  # Seu e-mail aqui
    
    if element_exists("//span[contains(text(), 'Digite seu número de celular ou nome de usuário')]"):
        locate_and_click("//input", 2)
        insert_data("//input", username) # Seu usuário aqui

    locate_and_click("(//input)[2]", 2)
    insert_data("(//input)[2]", password) # Sua senha aqui

    time.sleep(3)

except TimeoutException:
    print("O login não pode ser realizado no tempo limite")

# Bloqueia as contas verificadas
MAX_RETRIES = 3
def block_verified_accounts(tweet_aria, original_tweet_aria, verified_account):
    for attempt in range(MAX_RETRIES):
        try:
            tweet_element = verified_account.find_element(By.XPATH, ".//ancestor::article")
            tweet_aria = tweet_element.get_attribute("aria-labelledby")
            
            if tweet_aria == original_tweet_aria:
                return  # Pula se for o tweet original
            
            # Localiza e clica no botão de opções (caret)
            caret_button = tweet_element.find_element(By.XPATH, ".//button[@data-testid='caret']")
            time.sleep(2)
            caret_button.click()
            locate_and_click("//div[@data-testid='block']", 2)
            locate_and_click("(//span[contains(text(), 'Block')])[2]", 2)
            time.sleep(4)
            return  # Sucesso
        except StaleElementReferenceException:
            print("Elemento obsoleto, tentando novamente...")
            time.sleep(1)  # Pequeno atraso antes de tentar novamente
        except TimeoutException:
            print("Tempo limite ao tentar interagir com o elemento.")
            break
        except NoSuchElementException:
            print("Elemento não encontrado para a conta verificada.")
            break

# BLOQUEAR CONTAS VERIFICADAS
try:
    driver.get(tweet_link) # Link do tweet a ser bloqueado aqui
    wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='tweetText']")))
    driver.execute_script("window.scrollBy(0, 500);")

    no_verified_accounts = False
    original_tweet = driver.find_element(By.XPATH, "//article[@data-testid='tweet']")
    original_tweet_aria = original_tweet.get_attribute("aria-labelledby")
    
    # Enquanto houver contas verificadas
    while not no_verified_accounts:
        verified_accounts = driver.find_elements(By.XPATH, "//*[name()='svg' and @data-testid='icon-verified']")
        
        # Se não houver contas verificadas, sai do loop
        if not verified_accounts:
            no_verified_accounts = True    
        else:
            for verified_account in verified_accounts:
                block_verified_accounts(original_tweet_aria, original_tweet_aria, verified_account)

except TimeoutException:
    print("O tweet ou ícone de conta verificada não foi encontrado dentro do tempo limite.")
finally:
    driver.quit()

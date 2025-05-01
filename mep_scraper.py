from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
import time
import os
import requests

# ----------- CONFIGURACIÓN TELEGRAM -----------
TELEGRAM_TOKEN = 'TU_TOKEN_AQUI'
CHAT_ID = 'TU_CHAT_ID_AQUI'

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensaje}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"❌ Error al enviar notificación a Telegram: {str(e)}")

# ----------- CONFIGURACIÓN DE RUTA PARA ARCHIVO -----------
ruta_carpeta = os.path.join(os.getcwd(), "resultados")
if not os.path.exists(ruta_carpeta):
    os.makedirs(ruta_carpeta)
ruta_archivo = os.path.join(ruta_carpeta, "vacantes_encontradas.txt")

# ----------- CONFIGURAR SELENIUM EN MODO HEADLESS -----------
opciones = webdriver.ChromeOptions()
opciones.add_argument('--headless')
opciones.add_argument('--no-sandbox')
opciones.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=opciones)

# ----------- ABRIR PÁGINA -----------
driver.get("https://apps.mep.go.cr/formulario")
wait = WebDriverWait(driver, 10)
time.sleep(5)

# Obtener opciones de regional
select = driver.find_element(By.ID, "selectRegional")
options = select.find_elements(By.TAG_NAME, "option")

# Iterar sobre cada región
for i in range(1, len(options)):
    try:
        select = driver.find_element(By.ID, "selectRegional")
        options = select.find_elements(By.TAG_NAME, "option")
        option_text = options[i].text
        print(f"\n🔍 Revisando: {option_text}")
        options[i].click()
        time.sleep(5)

        pagina = 1
        encontrado = False

        while True:
            page_source = driver.page_source

            if "Estudios Sociales" in page_source:
                mensaje = f"📢 Vacante de Estudios Sociales encontrada en {option_text} (página {pagina})."
                print(f"✅ {mensaje}")
                enviar_telegram(mensaje)
                encontrado = True

                with open(ruta_archivo, "a", encoding="utf-8") as f:
                    f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {option_text} - Página {pagina}\n")

            try:
                boton_siguiente = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Next page"]')))
                driver.execute_script("arguments[0].scrollIntoView();", boton_siguiente)
                time.sleep(2)

                if not boton_siguiente.is_enabled():
                    break

                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Next page"]')))
                boton_siguiente.click()
                pagina += 1
                time.sleep(3)

            except (NoSuchElementException, TimeoutException, ElementClickInterceptedException):
                break

        if not encontrado:
            print(f"⚠️ No se encontraron vacantes de Estudios Sociales en {option_text}.")

        try:
            boton_primero = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Previous page"]')
            if boton_primero.is_enabled():
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Previous page"]')))
                boton_primero.click()
                time.sleep(2)
        except NoSuchElementException:
            pass

    except ElementClickInterceptedException as e:
        print(f"❌ Error al hacer clic en la región {option_text}: {str(e)}")
    except Exception as e:
        print(f"❌ Error inesperado en la región {option_text}: {str(e)}")

# ✅ Mensaje de finalización
enviar_telegram("✅ Búsqueda finalizada en todas las regionales. Puedes revisar el archivo de registro.")

driver.quit()



from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dataclasses import dataclass
import time
import requests

# Configuración Telegram
TELEGRAM_TOKEN = '7448542578:AAFTd9VT-CuMme0SAa1xhX4D08cr8pepywQ'
TELEGRAM_CHAT_ID = '-1002232864049'

def get_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    return chrome_options

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        requests.post(url, data=data)
    except Exception as e:
        print(f"Error enviando mensaje a Telegram: {e}")

@dataclass
class DynastyPlayer:
    name: str
    team: str
    position: str
    stats_vgood: list
    stats_elite: list
    roster_percent: str
    projection: str

def get_rotowire_top5():
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=get_chrome_options()
        )
        url = "https://www.rotowire.com/daily/nba/optimizer.php?site=FanDuel"
        driver.get(url)
        time.sleep(5)
        
        print("\n=== 🏀 TOP 5 JUGADORES ROTOWIRE 🏀 ===\n")
        send_telegram_message("\n=== 🏀 TOP 5 JUGADORES PARA HOY 🏀 ===\n")
        
        rst_xpath = "//*[@id='player-pool-table']/thead/tr/th[15]"
        rst_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, rst_xpath))
        )
        driver.execute_script("arguments[0].click();", rst_button)
        time.sleep(2)
        
        table = driver.find_element(By.ID, "player-pool-table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        top_5_data = []
        count = 0

        for row in rows:
            try:
                if count >= 5:
                    break
                    
                name_element = row.find_element(By.CLASS_NAME, "text-rw-500")
                name = name_element.text.strip()
                
                if name:
                    stats = row.find_elements(By.CLASS_NAME, "text-right")
                    roster_percent = stats[-1].text if len(stats) > 5 else "N/A"
                    projection_input = row.find_element(By.CSS_SELECTOR, "input.w-\\[50px\\].border.text-center.text-right")
                    projection = projection_input.get_attribute("value")
                    
                    top_5_data.append((name, roster_percent, projection))
                    count += 1
                    
            except Exception as e:
                continue
                
        return top_5_data
        
    except Exception as e:
        print(f"Error en Rotowire: {e}")
        send_telegram_message(f"❌ Error en Rotowire: {e}")
        return []
        
    finally:
        driver.quit()

def get_dynasty_stats(players_data):
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=get_chrome_options()
        )
        
        url = "https://hashtagbasketball.com/fantasy-basketball-dynasty-rankings"
        driver.get(url)
        time.sleep(10)
        
        print("\n=== 🏀 BUSCANDO ESTADÍSTICAS EN HASHTAG BASKETBALL 🏀 ===\n")
        
        wait = WebDriverWait(driver, 20)
        table_xpath = "//*[@id='UpdatePanel1']/div/div[3]/div[2]/div/div[3]/div/table"
        table = wait.until(EC.presence_of_element_located((By.XPATH, table_xpath)))
        
        found_players = []

        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows[1:]:
            try:
                name_element = row.find_element(By.CSS_SELECTOR, "td:nth-child(2)")
                player_name = name_element.text.strip()
                
                if any(search_name[0].lower() in player_name.lower() for search_name in players_data):
                    cols = row.find_elements(By.TAG_NAME, "td")
                    team = cols[4].text.strip()
                    position = cols[5].text.strip()
                    
                    stats = row.find_elements(By.TAG_NAME, "kbd")
                    stats_vgood = [s.text for s in stats if "vgood" in s.get_attribute("class")]
                    stats_elite = [s.text for s in stats if "elite" in s.get_attribute("class")]
                    
                    rotowire_data = next((data for data in players_data if data[0].lower() in player_name.lower()), None)
                    
                    player = DynastyPlayer(
                        name=player_name,
                        team=team,
                        position=position,
                        stats_vgood=stats_vgood,
                        stats_elite=stats_elite,
                        roster_percent=rotowire_data[1] if rotowire_data else "N/A",
                        projection=rotowire_data[2] if rotowire_data else "N/A"
                    )
                    
                    found_players.append(player)
                    
            except Exception as e:
                continue
                
        return found_players
        
    except Exception as e:
        print(f"Error en Hashtag Basketball: {e}")
        send_telegram_message(f"❌ Error en Hashtag Basketball: {e}")
        return []
        
    finally:
        driver.quit()

def main():
    print("Obteniendo top 5 jugadores de Rotowire...")
    top_5_data = get_rotowire_top5()
    
    if not top_5_data:
        mensaje = "❌ No se pudieron obtener jugadores de Rotowire"
        print(mensaje)
        send_telegram_message(mensaje)
        return
        
    print(f"\nJugadores encontrados en Rotowire: {', '.join(data[0] for data in top_5_data)}")
    
    print("\nBuscando estadísticas en Hashtag Basketball...")
    dynasty_players = get_dynasty_stats(top_5_data)
    
    print("\n=== 🏀 RESULTADOS FINALES 🏀 ===")
    
    for player in dynasty_players:
        elite_message = f"💫 Élite: {', '.join(player.stats_elite)}" if player.stats_elite else "⚠️ Este jugador no lidera en estadísticas élite"
        vgood_message = f"✨ Muy Bueno: {', '.join(player.stats_vgood)}" if player.stats_vgood else "⚠️ Este jugador no lidera en estadísticas muy buenas"
        
        mensaje = f"""
        🏀 Jugador: {player.name}
        🏢 Equipo: {player.team}
        📍 Posición: {player.position}
        📈 Roster %: {player.roster_percent}
        🎯 Proyección: {player.projection} FP
        
        {elite_message}
        {vgood_message}
        ➖➖➖➖➖➖➖➖➖➖➖➖
        """
        
        print(mensaje)
        send_telegram_message(mensaje)

if __name__ == "__main__":
    main()
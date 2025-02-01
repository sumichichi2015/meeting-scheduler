from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

def test_drag_delete():
    # ChromeDriverの設定
    driver = webdriver.Chrome()
    try:
        # アプリケーションを開く
        driver.get("http://localhost:3000")
        
        # ページが読み込まれるまで待機
        wait = WebDriverWait(driver, 10)
        
        # カレンダーから日付を選択
        calendar = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "vc-container")))
        days = calendar.find_elements(By.CLASS_NAME, "vc-day")
        # 最初の選択可能な日を選択
        for day in days:
            if "disabled" not in day.get_attribute("class"):
                day.click()
                break
        
        # 時間帯を設定
        start_time = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[v-model='defaultStartTime']")))
        start_time.send_keys("09:00")
        
        end_time = driver.find_element(By.CSS_SELECTOR, "select[v-model='defaultEndTime']")
        end_time.send_keys("17:00")
        
        # 全ての日に適用
        apply_button = driver.find_element(By.CLASS_NAME, "apply-time-button")
        apply_button.click()
        
        # ドラッグ操作のテスト
        time_slots = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "time-slot")))
        
        # 最初の時間帯から3つ目の時間帯までドラッグ
        actions = ActionChains(driver)
        actions.click_and_hold(time_slots[0])
        actions.move_to_element(time_slots[2])
        actions.release()
        actions.perform()
        
        # 削除されたかどうかを確認
        time.sleep(1)  # 変更が反映されるまで待機
        
        # 選択された時間帯が削除されているか確認
        remaining_slots = driver.find_elements(By.CSS_SELECTOR, ".time-slot.selected")
        print(f"Remaining selected slots: {len(remaining_slots)}")
        
        if len(remaining_slots) == 5:  # 8時間のうち3時間が削除されているはず
            print("Test passed: Time slots were successfully deleted")
        else:
            print("Test failed: Time slots were not deleted as expected")
            
    finally:
        # スクリーンショットを保存
        driver.save_screenshot("test_result.png")
        # ブラウザを閉じる
        driver.quit()

if __name__ == "__main__":
    test_drag_delete()

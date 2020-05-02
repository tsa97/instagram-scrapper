## LAST UPDATE 24042020
import sys
import re
import requests
import time
from bs4 import BeautifulSoup as BS
from selenium import webdriver
import pandas as pd
import collections



def remove_emoji(string):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

driver = webdriver.Chrome()

#Initial Scroll Setting
setting_scroll_awal = 30
setting_scroll_comment = 20
setting_press_load_more = 20

#login
username = "...."  ##insert user here
password = "...."  ##insert pass here
driver.get("https://www.instagram.com/accounts/login/")
time.sleep(3)

driver.find_element_by_xpath("//input[@name='username']").send_keys(username)
driver.find_element_by_xpath("//input[@name='password']").send_keys(password)
driver.find_element_by_xpath("//input[@name='password']").submit()
time.sleep(4)

account = "bankmandiri"

link = 'https://www.instagram.com/' + account

driver.get(link)

#........................
tryTime = 2
scroll = 0

shortcode_list_total = [] # Creating List for Shortcode

while scroll <= setting_scroll_awal: # While repeat initial scroll setting
    #............................
    # URL take
    html = driver.page_source
    soup = BS(html, "html.parser")
    # Ngasih tau shortcode mana aja yang dicapture di page ini
    shortcode = soup.find_all('a', href=lambda href: href and "/p/" in href)
    # Ngambil textnya dan naro di list bernama "shortcode_list_total"
    shortcode_list = [a['href'] for a in shortcode]
    # Merging List_total sama list yang hasil grab di page itu
    shortcode_list_total = shortcode_list_total + shortcode_list
    ### Reducing Duplication
    shortcode_list_total = list(set(shortcode_list_total))
    # print(shortcode_list_total)
    print(len(shortcode_list_total))
    #Check Duplication
    print("Duplication : " + str(len(shortcode_list_total) != len(set(shortcode_list_total))))


    #............................
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    print("Scrolling Public Post")
    time.sleep(tryTime)
    scroll += 1

#----------------------------------------------------------------------------
# Siapin list Buat Nampung Comment Comment
comment_list_total = []

# Narik data a dengan href link /p/
# Trus dikasih for loop biar ngelakuin untuk setiap URL
shortcode_stamp = 0
for x in shortcode_list_total:

    print("Found the URL : ", x)
    print("Processing URL (" + str(shortcode_stamp) + "/"+ str(len(shortcode_list_total)) +")")

    # MULAI MASUK KE POST
    driver.get('https://www.instagram.com/'+x)
    # driver.get('https://www.instagram.com/p/B_UpuRgpOuj/')
    time.sleep(2)

    tryTime = 2
    press = 0

    try:
        try:
            while press <= setting_press_load_more: # Clicking Plus Button
                #----------------------------------------------
                ### Nyomot Comment
                html = driver.page_source
                soup = BS(html, "html.parser")
                # Narik data a dengan href link /p/
                comment = soup.find_all('span', class_='')
                # Ngambil Textnya
                comment_list = [remove_emoji(span.text) for span in comment]
                comment_list_total = comment_list_total + comment_list
                ### Reducing Duplication
                comment_list_total = list(set(comment_list_total))

                # print(comment_list_total)
                print(len(comment_list_total))
                #Check Duplication
                print("Com_Duplication : " + str(len(comment_list_total) != len(set(comment_list_total))))
                #----------------------------------------------


                plus_button = driver.find_element_by_class_name('dCJp8.afkep')
                click_plus_button = plus_button.click()
                time.sleep(tryTime)
                press += 1
                print("Press Load More Button " + "(" + str(press+1) + "/" + str(setting_press_load_more+2) + ") in URL (" + str(shortcode_stamp) + "/"+ str(len(shortcode_list_total)) +")")


        except:
            while press <= setting_scroll_comment: # Scrolling Div Section
                #----------------------------------------------
                ### Nyomot Comment
                html = driver.page_source
                soup = BS(html, "html.parser")
                # Narik data a dengan href link /p/
                comment = soup.find_all('span', class_='')
                # Ngambil Textnya
                comment_list = [remove_emoji(span.text) for span in comment]
                comment_list_total = comment_list_total + comment_list
                ### Reducing Duplication
                comment_list_total = list(set(comment_list_total))

                # print(comment_list_total)
                print(len(comment_list_total))
                #Check Duplication
                print("Com_Duplication : " + str(len(comment_list_total) != len(set(comment_list_total))))
                #----------------------------------------------

                divBody  = driver.find_element_by_xpath("//div[@class='EtaWk']")
                driver.execute_script('arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;', divBody)
                print("Scrolling Comment Section")
                time.sleep(tryTime)
                press += 1
                print("Click Load More Button " + "(" + str(press+1) + "/" + str(setting_scroll_comment+2) + ")" + " in " + "URL (" + str(shortcode_stamp) + "/"+ str(len(shortcode_list_total)) +")")

    except IOError: # Error Handling
        try:
            sys.stdout.close()
        except IOError:
            pass
        try:
            sys.stderr.close()
        except IOError:
            pass

    shortcode_stamp += 1

#............................
# Exporting
df = pd.DataFrame(data={"Komentar": comment_list_total})
df.to_csv("mandiri_comment.csv", sep=',',index=False)

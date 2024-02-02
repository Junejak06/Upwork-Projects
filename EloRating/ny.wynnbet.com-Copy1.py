#!/usr/bin/env python
# coding: utf-8

# In[99]:


import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import pyautogui
from time import sleep
import pyperclip
    


# In[100]:


get_body = '''
var textArea = document.createElement("textarea");
textArea.value = document.body.outerHTML;
document.body.appendChild(textArea);
textArea.select();
document.execCommand("copy");
document.body.removeChild(textArea);
console.log("HTML body copied to clipboard.");

'''



# In[107]:


def getting_body_text():
    pyautogui.moveTo(x=1434, y=145, duration=0.7)
    pyautogui.click()
    pyautogui.moveTo(x=1511, y=305, duration=0.7)
    pyautogui.click()
    pyperclip.copy(str(get_body))
    pyautogui.hotkey('ctrl', 'v')  # Select all (Ctrl + A)
    pyautogui.press('enter')
    sleep(5)
    copied_text = pyperclip.paste()
    return copied_text
def change_url(url):
    pyautogui.moveTo(x=687, y=62, duration=0.7)
    pyautogui.click()
    pyautogui.hotkey('ctrl', 'a')  # Select all (Ctrl + A)
    pyautogui.press('delete')
    pyperclip.copy(str(url))
    pyautogui.hotkey('ctrl', 'v')  # Select all (Ctrl + A)
    pyautogui.press('enter')
def click_button(id_name):
    first_line = f"var gameButton = document.getElementById('{id_name}');"
    code_click =  '''
     if (gameButton) {
      gameButton.click();
    } else {
      console.log("Button with ID 'GAME' not found.");
    }
    '''
    full_code = first_line + code_click
    pyautogui.moveTo(x=1434, y=145, duration=0.7)
    pyautogui.click()
    pyautogui.moveTo(x=1511, y=305, duration=0.7)
    pyautogui.click()
    pyperclip.copy(str(full_code))
    pyautogui.hotkey('ctrl', 'v')  # Select all (Ctrl + A)
    pyautogui.press('enter')
    sleep(4)
def blank_row():
    blank_row = {
        "type": " ",
        "team1":" ",
        "team2":" ",
        "title": " ",
        "player":" ",
        "over1":" ",
        "over2":" ",
        "under1":" ",
        "under2":" ",
    }
    return blank_row
    


# In[102]:


change_url("https://ny.wynnbet.com/competition/115")
sleep(10)


# In[103]:


copied_text = getting_body_text()
soup = BeautifulSoup(copied_text, 'html.parser')


# In[104]:


divs  = soup.find_all("div", class_="eventItemLeft")
all_links = []
for div in divs:
    link= "https://ny.wynnbet.com" + div.find("a")["href"]
    cleaned_string = link.split('?')[0]
    all_links.append(cleaned_string)
    


# In[109]:


result = []
for link in all_links:
    change_url(link)
    sleep(30)
    copied_text = getting_body_text()
    sleep(3)
    soup = BeautifulSoup(copied_text, 'html.parser')
    buttons = soup.find("div", class_="tabToggle")
    print(buttons.text)
    if "Passing" in buttons.text:
        print("Passing availble")
        url = all_links[0] + passing
        click_button("PASSING")
        copied_text = getting_body_text()
        soup = BeautifulSoup(copied_text, 'html.parser')
        teamComponent = soup.find("div", class_="teamComponent")
        teamTexts = teamComponent.find_all("span", class_="teamText")
        team1 = teamTexts[0].text
        team2 = teamTexts[1].text
        main_contetnt_div = soup.find("div", class_="marketContainer pb-md-2")
        eventTables = main_contetnt_div.find_all("div", class_="eventTable")
        for i in eventTables:
            bold = i.find("div", class_="bold")
            if bold:
                title = bold.text
                teamNs = i.find_all("div", "teamN")
                for teamN in teamNs:
                    player = teamN.find("div", class_="eventItemName").text
                    spans = teamN.find_all("span")
                    over1 = spans[0].text
                    over2 = spans[1].text
                    under1 = spans[2].text
                    under2 = spans[3].text
                    result.append({
                            "type": "PASSING",
                            "team1":team1,
                            "team2":team2,
                            "title": title,
                            "player":player,
                            "over1":over1,
                            "over2":over2,
                            "under1":under1,
                            "under2":under2,
                        })    
        result.append(blank_row())
        sleep(10)


    if "Rushing" in buttons.text:
        print("Rushing availble")
        click_button("RUSHING")
        copied_text = getting_body_text()
        soup = BeautifulSoup(copied_text, 'html.parser')
        teamComponent = soup.find("div", class_="teamComponent")
        teamTexts = teamComponent.find_all("span", class_="teamText")
        team1 = teamTexts[0].text
        team2 = teamTexts[1].text
        main_contetnt_div = soup.find("div", class_="marketContainer pb-md-2")
        eventTables = main_contetnt_div.find_all("div", class_="eventTable")
        for i in eventTables:
            bold = i.find("div", class_="bold")
            if bold:
                title = bold.text
                teamNs = i.find_all("div", "teamN")
                for teamN in teamNs:
                    player = teamN.find("div", class_="eventItemName").text
                    spans = teamN.find_all("span")
                    over1 = spans[0].text
                    over2 = spans[1].text
                    under1 = spans[2].text
                    under2 = spans[3].text
                    result.append({
                            "type": "RUSHING",
                            "team1":team1,
                            "team2":team2,
                            "title": title,
                            "player":player,
                            "over1":over1,
                            "over2":over2,
                            "under1":under1,
                            "under2":under2,
                        })

        result.append(blank_row())
        sleep(10)
    if "Receiving" in buttons.text:
        print("Receiving availble")
        click_button("RECEIVING")
        copied_text = getting_body_text()
        soup = BeautifulSoup(copied_text, 'html.parser')
        teamComponent = soup.find("div", class_="teamComponent")
        teamTexts = teamComponent.find_all("span", class_="teamText")
        team1 = teamTexts[0].text
        team2 = teamTexts[1].text
        main_contetnt_div = soup.find("div", class_="marketContainer pb-md-2")
        eventTables = main_contetnt_div.find_all("div", class_="eventTable")
        for i in eventTables:
            bold = i.find("div", class_="bold")
            if bold:
                title = bold.text
                teamNs = i.find_all("div", "teamN")
                for teamN in teamNs:
                    player = teamN.find("div", class_="eventItemName").text
                    spans = teamN.find_all("span")
                    over1 = spans[0].text
                    over2 = spans[1].text
                    under1 = spans[2].text
                    under2 = spans[3].text
                    result.append({
                            "type": "RECEIVING",
                            "team1":team1,
                            "team2":team2,
                            "title": title,
                            "player":player,
                            "over1":over1,
                            "over2":over2,
                            "under1":under1,
                            "under2":under2,
                        })
        result.append(blank_row())
        sleep(10)


# In[110]:


df = pd.DataFrame(result)
df


# In[111]:


df.to_excel(r"C:\Users\kjuneja\OneDrive\7777.xlsx")


# In[ ]:





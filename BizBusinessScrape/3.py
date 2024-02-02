all_data = []

# Logic to get all industry checkboxes
industry_checkboxes = driver.find_elements(By.XPATH, 
                                           "//input[contains(@type,'checkbox') and contains(@name,'Industry')]")

# Iterating over all industry checkboxes
for checkbox in industry_checkboxes:
    try:
        checkbox.click()
        time.sleep(2)

        # Click apply button
        apply_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Apply')]")
        apply_button.click()
        time.sleep(5)

        listing_xpath = ("/html[1]/body[1]/main[1]/div[1]/app-root[1]/app-bfs-search-results[1]/div[1]/"
                         "section[2]/app-bfs-listing-container[1]/div[1]/app-listing-diamond[1]/a[1]/div[1]/"
                         "div[1]/div[1]/div[1]/div[1]/swiper[1]/div[3]/div[1]")
        driver.find_element(By.XPATH, listing_xpath).click()
        time.sleep(5)

        title = driver.find_element(By.XPATH, "//h1[@class='bfsTitle']").text
        location_text = driver.find_element(By.XPATH, "//h2[@class='gray']").text
        city, state = location_text.split(",")[0], location_text.split(",")[1].strip().split(" ")[0]
        country = "USA"
        url = driver.current_url
        source = "bizquest"

        # Scrape Listed By (Firm)
        try:
            firm_xpath = ("/html[1]/body[1]/form[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/"
                          "div[1]/div[1]/div[1]/div[1]/div[2]/div[3]/h4[1]/span[1]")
            listed_by_firm_element = wait.until(EC.presence_of_element_located((By.XPATH, firm_xpath)))
            listed_by_firm = listed_by_firm_element.text
        except TimeoutException:
            listed_by_firm = "No Firm Listed"
        
        print("Listed By (Firm):", listed_by_firm)

        # Scrape Listed By (Name) - First Way
        try:
            name_xpath_1 = ("/html[1]/body[1]/form[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/"
                           "div[1]/div[1]/div[1]/div[1]/div[2]/div[3]/h3[1]/a[1]")
            listed_by_name_element = wait.until(EC.presence_of_element_located((By.XPATH, name_xpath_1)))
            listed_by_name = listed_by_name_element.text
        except TimeoutException:
            try:
                # Scrape Listed By (Name) - Second Way
                name_xpath_2 = ("/html[1]/body[1]/form[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/"
                               "div[1]/div[1]/div[1]/div[1]/div[2]/div[3]/h3[1]")
                listed_by_name_element = wait.until(EC.presence_of_element_located((By.XPATH, name_xpath_2)))
                listed_by_name = listed_by_name_element.text
            except TimeoutException:
                listed_by_name = "No Name Listed"
        
        print("Listed By (Name):", listed_by_name)

        # Click to reveal phone number
        view_telephone_xpath = ("/html[1]/body[1]/form[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/"
                                "div[1]/div[1]/div[1]/div[1]/div[2]/div[3]/h3[1]/div[1]/a[1]")
        driver.find_element(By.XPATH, view_telephone_xpath).click()
        time.sleep(2)

        phone_xpath = ("/html[1]/body[1]/form[1]/div[2]/div[2]/div[1]/div[1]/div[1]/div[1]/div[3]/div[2]/div[1]/"
                       "div[1]/div[1]/div[1]/div[2]/div[3]/h3[1]/div[1]/label[1]/a[1]")
        phone = driver.find_element(By.XPATH, phone_xpath).text
        print(f"Phone Number: {phone}")

        data = {
            "Title": title,
            "City": city,
            "State": state,
            "Country": country,
            "URL": url,
            "Industry": industry.text,
            "Source": source,
            "Description": description,
            "Listed By (Firm)": listed_by_firm,
            "Listed By (Name)": listed_by_name,
            "Phone": phone
        }

        all_data.append(data)

        driver.back()
        time.sleep(5)

        # Reset the industry filter
        driver.find_element(By.XPATH, filter_xpath).click()
        time.sleep(2)
        driver.find_element(By.XPATH, more_industries_xpath).click()
        time.sleep(2)

    except NoSuchElementException:
        print("Could not process an industry checkbox. Skipping to the next one.")
        continue

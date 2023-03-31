# This python program gets all the saved passwords, history, downloads, cookies 
! caution: only retrive from chromium based browser like chrome, ms-edge

To run the program install requirements.txt 
to install requirements.txt run: pip install -r requirements.txt
then run the .py file

Examples:
Retrive all installed browsers data

for browser in installed_browsers():
    browser_path = browsers[browser]
    
    br = BrowserData(browser_path)

    logins_data = br.get_login_data() #will return nested list
    history = br.get_web_history()
    cookies = br.get_cookies()
    downloads = br.get_download_history()

to get returned data as dict provide return_type:
logins_data = br.get_login_data(return_type='dict')


To save returned data into a file:
for browser in installed_browsers():
    browser_path = browsers[browser]

    br = BrowserData(browser_path)
    data = br.get_login_data(return_type='list')
    content = ''
    for item in data:
        content += str(item) + '\n'
    br.save_to_file(browser, 'login_data', content)
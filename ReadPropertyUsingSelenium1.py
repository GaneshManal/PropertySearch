'''
Created on Nov 10, 2015

@author: manal_g
'''
from selenium import webdriver
import sys, time
import os
from selenium.webdriver.support.ui import WebDriverWait
from BeautifulSoup import BeautifulSoup, Tag
import csv
import requests
import codecs
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

reload(sys)
sys.setdefaultencoding('utf-8')

try:
    year, district, village, cts_no = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] 
except:
    print 'Usage - python ReadProperyUsingSelenium1.py year district village cts_no'
    sys.exit(0)

header = ['Year', 'District', 'Village','CTS No', 'DocNo', 'DName', 'RDate', 'SROName', 'Seller Name', 'Purchaser Name', 'Property Description', 'SROCode', 'Status']
records = []
record_sr = 0
def scan_content(content, link_buttons):
    print "-- link_buttons -->", len(link_buttons)
    soup = BeautifulSoup(content)
    tables = soup.find("table", {"id" : "RegistrationGrid"})
    if tables is None:
        return None

    for x_table in tables:
        if type(x_table) is not Tag:
            continue

        row_count = 0
        for x_row in x_table.findAll('tr'):
            cols = x_row.findAll('td')
            if len(cols) == 11:
                row_count += 1
                print '--- Row-%0d ---'%(row_count)
                data_cols = [cols[i].text.strip().replace('\n','/') for i in range(9) ]

                window_before = driver.window_handles[0]
                #GAMGAM : 22 Jan
                if len(driver.find_elements_by_class_name("Button")) < row_count+1:
                    return True

                driver.find_elements_by_class_name("Button")[row_count+1].click()
                time.sleep(10)

                while True:    
                    if len(driver.window_handles) == 2:
                        break
                    time.sleep(5)

                window_after = driver.window_handles[1]
                driver.switch_to_window(window_after)

                '''
                with open('temp.tst', 'w') as f:
                    f.write(driver.page_source.encode('utf-8').strip())
                driver.close()
                '''
                #START
                soup = BeautifulSoup(driver.page_source.encode('utf-8').strip())
                link_tables = soup.find("table", {"cellpadding" : "5"})
                x = 0
                col1, col2 = [], []
                if link_tables is not None:
                    for xitem in link_tables:
                        if 'name' not in dir(xitem):
                            continue

                        for yitem in xitem:
                            if 'name' not in dir(xitem):
                                continue

                            for zitem in yitem:
                                if 'text' not in dir(zitem):
                                    continue

                                for col in zitem:
                                    #if 'name' not in dir(col):
                                    #    continue
                                    x += 1

                                    if 'zfill' in dir(col):
                                        if col.title().strip() == '':
                                            col1.append('-')
                                            continue

                                        col1.append(col.title().strip())
                                        continue

                                    col2.append(col.text.strip())
                else:
                    print '*'*50
                data_cols.extend(col1)
                driver.close()
                #END
                driver.switch_to_window(window_before) 
                if '...' in data_cols:
                    continue

                trans_cols = []
                for item in range(len(data_cols)):
                    if item in [1, 4, 5, 6]:
                        url="https://www.googleapis.com/language/translate/v2?key=AIzaSyCaB8lyIuCy-KtDTank67KYMi_4-1sCT6c&q="+ data_cols[item]  +"&source=hi&target=en"
                        response = requests.get(url)
                        print response.status_code
                        if response.status_code != 200:
                            trans_cols.append('cannot be translated')
                        else:
                            #print 'translated--->', eval(response.text)['data']['translations'][0]['translatedText']
                            trans_cols.append(eval(response.text)['data']['translations'][0]['translatedText'])
                    else:
                        trans_cols.append(data_cols[item])

                #records.append(trans_cols)
                with codecs.open(os.getcwd() + os.path.sep + 'output' + os.path.sep + 'data_'+year+'_'+village+'_'+cts_no.replace('/','-')+'.csv', 'a', 'utf-8') as csvfile:
                    combine_details = [year, district, village, cts_no]
                    combine_details.extend(trans_cols)
                    writeData = '@'.join(combine_details)
                    csvfile.write('\n' + str(writeData).decode('utf-8', 'ignore'))


                if row_count == 10:
                    break
    return True


driver = webdriver.Chrome()
driver.get("https://esearchigr.maharashtra.gov.in/testingesearch/wfsearch.aspx")

element0 = driver.find_element_by_name("ddlFromYear")
element0.send_keys("2015")

element1 = driver.find_element_by_id('ddlDistrict')
for option in element1.find_elements_by_tag_name('option'):
    if option.get_attribute('value') == '30':
        option.click()
        break

element2 = driver.find_element_by_name("txtAreaName")
#driver.execute_script('window.stop()')
element2.clear()
element2.send_keys(village[:4])

driver.implicitly_wait(10)
element3 = driver.find_element_by_name("ddlareaname")
element3.click()
#print "clicked dropdown 1"

time.sleep(5)
element2 = driver.find_element_by_name("txtAreaName")
element2.send_keys(village[:4]+ Keys.RETURN)

driver.implicitly_wait(10)
element3 = driver.find_element_by_name("ddlareaname")
element3.click()
time.sleep(5)

element3 = driver.find_element_by_id('ddlareaname')
for option in element3.find_elements_by_tag_name('option'):
    #print '--option-->',option.get_attribute('value')
    if option.get_attribute('value').lower() == village.lower():
        #print 'selected'
        option.click()
        break

time.sleep(5)
element3 = driver.find_element_by_id('txtAttributeValue')
element3.send_keys(cts_no)
driver.find_element_by_name('btnSearch').click()

print "CTS No - ",cts_no
time.sleep(15)
details, rec_count = [], -1
page_count = 1
first_page, more_page_flag = True, False
while(True):
    if not first_page:
        time.sleep(5)

    index_links = driver.find_elements_by_class_name("Button")
    scan_content(driver.page_source.encode('utf-8').strip(), index_links)
    page_links = []
    for x_page in [ str(x) for x in range(page_count+1, page_count+10)]:
        page_links = driver.find_elements_by_link_text(str(x_page))
        print "x_page, page_links |", x_page, len(page_links)
        if len(page_links) == 0:
            break
        for x_link in page_links:
            x_link.click()
            time.sleep(3)
            index_links = driver.find_elements_by_class_name("Button")
            ret = scan_content(driver.page_source.encode('utf-8').strip(), index_links)

            if ret is None:
                break

            continue
    if len(page_links) == 0:
        break
        

    more_links = driver.find_elements_by_link_text('...')
    more_count = len(more_links)

    print "first page , more count", first_page, more_count
    cont_flag = False
    if first_page: 
        if more_count:
            first_page = False
            more_links = driver.find_elements_by_link_text('...')
            for x_link in more_links:
                print 'paginatin first --->', x_link.text.encode('utf-8')
                if x_link.text.encode('utf-8') == '...':
                    page_count += 10
                    x_link.click()
                    #print "slept for 2 secs & continued"
                    cont_flag = True
                    break
            if cont_flag:
                continue
        else:
            break

    first_skipped = False
    if more_count > 1:
        more_links = driver.find_elements_by_link_text('...')
        for x_link in more_links:
            if x_link.text.encode('utf-8') == '...':
                if first_skipped:
                    print 'paginatin second --->', x_link.text.encode('utf-8')
                    page_count += 10
                    x_link.click()
                    #print "slept for 2 secs & continued"
                    cont_flag = True
                    break
                first_skipped = True
                #print 'skipped first ...'
        if cont_flag:
            continue
    else:
        break
'''
print "writing csv file"
with codecs.open(os.getcwd() + os.path.sep + 'output' + os.path.sep + 'data_'+year+'_'+village+'_'+cts_no+'.csv', 'w', 'utf-8') as csvfile:
    for x_record in records:
        combine_details = [year, district, village, cts_no]
        combine_details.extend(x_record)
        csvfile.write('\n' + '@'.join(combine_details))
'''
driver.close()
print "Driver Close.. Exiting"
sys.exit(0)
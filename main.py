'''
Author: Jorge Andres Bravo
Author's Github: https://github.com/jazzify
Author's Email: jm1218@hotmail.com

Creation Date: 27/06/17
Last modification date: 12/01/2018

Description: This script was created for time optimization of the CoE team in Himalaya                Digital Agency.
             It looks for the right links the user have to work with
             and it organizes them into a directory.

- input file_name: gets static site name (ex: static-15) and uses it to name the .txt and .xml files
- input domain: gets the site domain and uses it to connect to svn.colgate
- input suffix: get the suffix domain to get a list of links
'''

import os # Required for creating directories and files.
import urllib # Package that collects several modules for working with URLs
import requests # Required for reading each site content.
import re # Required for regular expressions use.
from urllib.error import HTTPError # Required for handle the 404 exception.


# LISTS VARIABLES
working = []
not_working = []
working_under_stage = []
xml_links = []
weird_code = []
redirected = []

# VARIABLES
file_name = input("Static name (ex: static-12): ").upper()
domain = input("Domain (ex: www.meridol.cz): ")
suffix = input("Suffix (ex: /app/meridol/CZ/ ): ")
principal_url = "https://svn.colgate.com/siteurls/%s-withoutquery.urls.txt" % (domain)
headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.86 Safari/537.36' }
matching_sites = 0
gif_sites = 0
patt = "<p>com.colgate.cpvignette.VignetteChannelException:"  # Pattern found in all not working sites and some working under stage only.
patt2 = "<p>java.lang.ArrayIndexOutOfBoundsException</p>" # Pattern found in some working under stage only sites.
exclude_urls = ('.gif', '.png', '.jpg', '.jpeg', '.pdf', '.sql', '.css', '.js', '.xml', '.txt', '.svg', '.eot', '.ttf', '.woff', '.7z', '.bz2', '.gz', '.rar', '.bzip2', '.gzip', '.tgz', '.zip', '.ico', '.tar')

domain = 'http://'+domain  # New domain for the .xml file.


req = urllib.request.Request(principal_url, headers=headers)  # CONNECTION WITH SVN.COLGATE
response = urllib.request.urlopen(req) 
site = response.read().decode() # Reads the site content.
site_links = site.split() # Splits every link...


for url in site_links:
    if re.search(r'^%s%s' % (domain, suffix), url):
        matching_sites += 1
        if url.endswith(exclude_urls):
            gif_sites += 1
        elif url.endswith('/'):
            weird_code.append(url) # Generally white pages or just JS code.
        else:
            try:
                request = requests.get(url, headers = headers) # Try to connect to each URL
                status_code = request.history  # Returns each site status
                if status_code:
                    for x in status_code:
                        redirected.append((request.url, x.url))
                elif re.search(patt, request.text):
                        not_working.append(url)
                else:
                    if re.search(patt2, request.text):
                        working_under_stage.append(url)
                    else:
                        working.append(url)
                        
                    xml_links.append(url)
                        
            except urllib.error.HTTPError as e:
                print(e)
                weird_code.append(url)
                
            except urllib.error.URLError as e:
                print(e)
                continue


print('\nMatched URLs: ', matching_sites)
print('\nWorking URLs: ', len(working))
print('\nWorkingUnderStage URLs: ', len(working_under_stage))
print('\nRedirected URLs: ', len(redirected))
print('\nNot Working URLs: ', len(not_working))
print('\nWhite page URLs: ', len(weird_code))
print('\nImages URLs: ', gif_sites)
        

os.mkdir(file_name) # Creates a new directory.


file = open(file_name+'/xml-links-'+file_name + '.txt', 'w') # Creates a .txt file inside the directory with the links info.

file.write('************************** ORIGINAL LINK **************************')
file.write('\n\n\n************************** WORKING LINKS **************************\n')
for link in working:
    file.write(link+'\n')  # Add all working links to the working list for its future use.

file.write('\n\n\n************************** WORKING UNDER STAGE ONLY **************************\n')
for link in working_under_stage:
    file.write(link+'\n') # Add all working under stage links to the working list for its future use.

file.write('\n\n\n************************** REDIRECTED LINKS **************************\n')
for link, x in redirected:
    file.write('From: ' + x + '\n\tTo:' + link + '\n\n') # Add all redirected.
    
file.write('\n\n\n************************* NOT WORKING LINKS **************************\n')
for link in not_working:
    file.write(link+'\n') # Add all not working links to the working list for its future use.
for link in weird_code:
    file.write(link+'\n') # Add all weird links to the working list for its future use.
    
file.close()  # Close and save the .txt file.



file2 = open(file_name+'/suite-'+file_name.lower()+'.xml', 'w') # Creates a new .xml file with the respective working links.
# Writes the .xml file template for jenkins process
file2.write("""<?xml version="1.0" encoding="UTF-8"?> 
<suite name="dragonfly-aet-static-migration-"""+file_name.lower()+"""" company="colgate-palmolive" project="dragonfly-static" domain=\""""+domain+"""">
    <test name="dragonfly-aet-static-migration-"""+file_name.lower()+"""" useProxy="rest">
        <collect>
            <header key="Authorization" value="Basic dm1sY29sZ2F0ZTp0b290aHBhc3Rl" />
            <modify-cookie action="add" cookie-name="cookies_allowed" cookie-value="1" />
            <open/>
            <wait-for-page-loaded/>
            <resolution width="1920" height="1080" name="desktop" />
            <sleep duration="2000" />
            <screen name="desktop" />
            <resolution width="970" height="1080" name="medium" />
            <sleep duration="2000" />
            <screen name="medium" />
            <resolution width="768" height="1080" name="tablets" />
            <sleep duration="2000" />
            <screen name="tablets" />
            <resolution width="480" height="1080" name="phone" />
            <sleep duration="2000" />
            <screen name="phone" />
            <source/>
            <status-codes/>
            <js-errors/>
        </collect>
        <compare>
            <screen comparator="layout" />
            <source comparator="source" compareType="markup" />
            <status-codes filterRange="400,600">
            </status-codes>
            <js-errors/>
        </compare>
        <urls>\n""")

for url in xml_links:
    file2.write("<url href='"+url[len(domain):]+"'/>\n") # Adds every working link without the domain.

file2.write("""\n</urls>
    </test>
</suite>""")

file2.close()  # Close and save the .xml file


# CHANGES .TXT FILE
filechanges = open(file_name+'/CHANGES-'+file_name + '.txt', 'w') # Creates a .txt file inside the directory with the links info.

for link in working:
    filechanges.write('*'+link+'*\n')  # Add all working links to the working list for its future use.
    filechanges.write(' - Omniture commented from lines xxxx to xxxx\n\n')

filechanges.close()
# END CHANGES .TXT FILE

input("\nDone...")

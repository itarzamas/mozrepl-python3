import mozrepl
import re
import urllib

mozrepl = mozrepl.Mozrepl()
# mozrepl.execute('alert("queso")')

# mozrepl.openUrl('https://www.amazon.es/s/ref=sr_st_price-asc-rank?keywords=dragon+ball&rh=n%3A599385031%2Ck%3Adragon+ball&__mk_es_ES=%C3%85M%C3%85Z%C3%95%C3%91&qid=1465736604&sort=price-asc-rank')

url1 = mozrepl.getElement('/html/body/div[1]/div[1]/div[2]/div[1]/ul/li[1]/a/div/div[2]/h5', 'xpath')
# res = mozrepl.getElement('//*[@id="resultItems"]/li[1]/a/div/div[2]/h5', 'xpath')

html_read = mozrepl.readHTML()
images = re.findall('data-a-hires="(https://.+?_SL1500_.jpg)',html_read)

if images:
	for image in images:
		urllib.urlretrieve(image, "00000001.jpg")

# print(res.click())


'''
//*[@id="resultItems"]/li[1]/a/div/div[2]/h5

//*[@id="resultItems"]/li[2]/a/div/div[2]/h5


//*[@id="anonCarousel2"]/ol/li[1]/div/div/div/img = Imagen Full
Get images = https://(.+?)_SL1500_.jpg

price=
Precio=
//*[@id="priceblock_ourprice"]

envio=
//*[@id="ourPrice_availability"]/span 
'''

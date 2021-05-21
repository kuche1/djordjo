#!/usr/bin/env python3

import requests
import tempfile
import subprocess
import shlex

import bs4


BASE_URL = 'https://www.pizzadjordjo.com/'
URL = BASE_URL + '?page={}'
FIRST_PAGE = URL.format(1)

filter_ing = ['пушено пилешко филе']


class Pizza:
    def __init__(s, name, ing, weight, size, price, image_link):
        s.name = name
        s.ing = ing
        s.weight = weight
        s.size = size
        s.price = price
        s.value = weight / price
        s.image_link = image_link

        s.image_cached = False
        s.image_path = None

    def show_info(s):
        print(s)

    def show_image(s):
        if not s.image_cached:
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(get_response(s.image_link))
                s.image_path = f.name
        display_image(s.image_path)

    def __repr__(s):
        res = f'''{s.value} -> {s.name}
\t{s.size}
\t{s.ing}
\t{s.weight}
\t{s.price}
\t{s.image_link}
'''
        return res


def display_image(path):
    # viu icat
    subprocess.call(shlex.join(['viu', path]), shell=True)

def get_response(url):
    page = requests.get(url)
    assert page.ok
    return page.content

def get_number_of_pages(url):
    resp = get_response(url)
    soup = bs4.BeautifulSoup(resp, "lxml")
    res = soup.find_all(class_='pagination')[0] # could have used .find(...)
    text = res.text
    assert text.startswith('«')
    text = text[1:]
    assert text.endswith('»')
    text = text[:-1]

    page_num = 1
    while text.startswith(str(page_num)):
        text = text[len(str(page_num)):]
        page_num += 1
    assert page_num != 1
    page_num -= 1
    return page_num


pages = get_number_of_pages(FIRST_PAGE)
print(f'Pages: {pages}')
print()

pages_data = []
for page_num in range(1, pages+1):
    pages_data.append(get_response(URL.format(page_num)))

for page in pages_data:
    soup = bs4.BeautifulSoup(page, "lxml")

    pizzas = soup.find_all(class_='product-detail-more')

    for pizza_ind, pizza in enumerate(pizzas):
        name = pizza.find(class_='product-name').text.strip()
        #print(name)
        
        ings = pizza.find_all(class_='product-ingredients')
        for ind, ing in reversed(list(enumerate(ings))):
            ing = ing.text.strip()
            if ing == '':
                del ings[ind]
            else:
                ing = ing.split(', ')
                ings[ind] = ing
        l = len(ings)
        if l == 0:
            ing = 'NO_DESC'
        elif l == 1:
            ing = ings[0]
        else:
            ing = sum(ings, [])
            
        for ind,_ing in enumerate(ing):  
            ing[ind] = _ing.replace('\n', ' ; ')


        weight, size, price = pizza.find_all(class_='row product-unit')[-1].text.split('\n')[1:4]

        postfix1 = ' гр.'
        postfix2 = ' бр.'
        assert weight.endswith(postfix1) or weight.endswith(postfix2)
        assert len(postfix1) == len(postfix2)
        weight = weight[:-len(postfix1)]
        assert float(weight) == int(weight)
        weight = int(weight)

        postfix = ' лв.'
        assert price.endswith(postfix)
        price = price[:-len(postfix)]
        price = float(price)

        image = pictures = soup.find(class_='img-responsive', title=name)
        if image == None:
            #image_link = 'error'
            image = pictures = soup.find(class_='img-responsive', title=' '+name)
        image = image['src']
        image_link = BASE_URL + image
        
        pizzas[pizza_ind] = Pizza(name, ing, weight, size, price, image_link)


for ind, pizza in reversed(list(enumerate(pizzas))):
    for ing in filter_ing:
        if ing in pizza.ing:
            break
    else:
        continue

    del pizzas[ind]

pizzas.sort(reverse=True, key=lambda p:p.value)

for pizza in pizzas:
    pizza.show_info()
    pizza.show_image()
    input()




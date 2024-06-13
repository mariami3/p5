from flask import Flask, request, render_template, url_for, redirect
from web3 import Web3
import re
from web3.middleware import geth_poa_middleware 
from contract_info import abi, contract_address

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
contract = w3.eth.contract(address=contract_address, abi=abi)
account = ""

app = Flask(__name__)



@app.route("/")
def home():
    return render_template('index.html')

def check(password):
    if len(password) < 12:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        return False
    if re.search(r"password123|qwerty123", password, re.IGNORECASE):
        return False
    return True

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        password = request.form['password']
        if check(password):
            account = w3.geth.personal.new_account(password)
            # Убедитесь, что у вас есть достаточно средств и разблокирован аккаунт для отправки транзакции
            # w3.geth.personal.unlock_account(account, password)
            # w3.eth.send_transaction(
            #     {"to": account, "from": w3.eth.accounts[0], "value": w3.toWei(1, 'ether')})
            
            print(f"Публичный ключ: {account}")
            return redirect('/authorized')
        else:
            return render_template('register.html', error='Пароль недостаточно надежный')
    return render_template('register.html')

@app.route('/authorized', methods=['GET', 'POST'])
def authorized():
    if request.method == 'POST':
        publicKey = request.form['publicKey']
        password = request.form['password']
        # Убедитесь, что у вас есть правильные данные для разблокировки аккаунта
        # w3.geth.personal.unlock_account(publicKey, password)
        print("Авторизация успешна!")
        return redirect('/logout')
    return render_template('authorized.html')

@app.route('/logout')
def logout():
    return render_template('logout.html')



@app.route('/authorized/button/createEstate')
def createEstate():
    try:
        address = input("Введите адрес: ")
        square = int(input("Введите площадь: "))
        type = int(input("Введите один из типо недвижимости:  1. House, 2. Flat, 3. Loft, 4. Dacha : "))
        tx = contract.functions.createEstate(address, square, type).transact({
            'from': account
        })
        print("Недвижимость успешно создана")

    except Exception as e:
        print("Ошибка создания недвижимости", e)


@app.route('/authorized/button/createAD')
def createAD():
    try:
        price = int(input("Введите цену: "))
        idEstate = int(input("Введите номер недвижимости: "))

        contract.functions.createAd(price, idEstate).transact({
            'from': account
        })
        print("Успешное создание объявления")
    except Exception as e:
        print("Ошибка добавления недвижимости: ", e)


@app.route('/authorized/button/changeEstate')
def changeEstate():
    try:
        idEstate = int(input("Введите номер недвижимости: "))
        contract.functions.updateEstateActive(idEstate).transact({
            'from': account
        })
        print("Объявление успешно обновлено")
    except Exception as e:
        print("Ошибка обновления недвижимости: ", e)


@app.route('/authorized/button/changeAD')
def changeAD():
    try:
        idAD = int(input("Введите номер объявления: "))
        contract.functions.updateAdType(idAD).transact({
            'from': account
        })
        print("Успешное обновление объявления")
    except Exception as e:
        print("Ошибка обновления объявления: ", e)


@app.route('/authorized/button/buyEstate')
def buyEstate():
    try:
        idAD = int(input("Введите номер объявления: "))
        contract.functions.buyEstate(idAD).transact({
            'from': account
        })
        print("Недвижимость успешна куплена")
    except Exception as e:
        print("Ошибка покупки недвижимости: ", e)


@app.route('/authorized/button/withdraw')
def withdraw():
    try:
        amount = int(input("Введите количество средств: "))
        if(amount > 0) and (amount <= w3.eth.get_balance(contract_address)):
            contract.functions.withdraw(amount).transact({
            'from': account,
            'value': amount
            })
        print("Деньги успешно выведены с баланса контракта")
    except Exception as e:
        print("Ошибка вывода средств: ", e)


@app.route('/authorized/button/pay')
def pay():
    try:
        amount = int(input("Введите количество средств: "))
        contract.functions.pay().transact({
                'from': account,
                'value': amount
            })
        print("Деньги есть")
    except Exception as e:
        print("Ошибка: ", e)


@app.route('/authorized/button/get')
def getEstates():
    try:
        available_estates = contract.functions.getAvailableEstates().call()
        for estate in available_estates:
            print(f"ID: {estate[5]}, Адрес: {estate[0]}, Площадь: {estate[1]}, Тип: {estate[2]}")
    except Exception as e:
        print("Ошибка получения информации о доступных недвижимостях: ", e)
def getAD():
    try:
        open_ads = contract.functions.getOpenAdvertisements().call()
        for ad in open_ads:
            print(f"ID: {ad[1]}, Цена: {ad[0]}, Тип объявления: {ad[5]}")
    except Exception as e:
        print("Ошибка получения информации о текущих объявлениях: ", e)
def getBalance(account):
    try:
        balance = contract.functions.balances(account).call()
        print(f"Баланс на контракте для {account}: {balance}")
    except Exception as e:
        print("Ошибка получения баланса на контракте: ", e)
def getAccountBalance(account):
    try:
        balance = w3.eth.get_balance(account)
        print(f"Баланс на аккаунте {account}: {balance}")
    except Exception as e:
        print("Ошибка получения баланса на аккаунте: ", e)


if __name__ == '__main__':
    app.run(debug=True) 
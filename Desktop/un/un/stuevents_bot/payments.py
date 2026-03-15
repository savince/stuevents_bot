import uuid
from urllib.parse import urlencode
from config import YOOMONEY_RECEIVER

def create_payment_url(amount: float, description: str, label: str = None):
    
   # Генерирует ссылку на оплату через ЮMoney

    
    if label is None:
        label = str(uuid.uuid4())[:8]
    
    params = {
        'receiver': YOOMONEY_RECEIVER,           # номер кошелька
        'quickpay-form': 'shop',                  # форма оплаты
        'targets': description,                    # назначение платежа
        'paymentType': 'AC',                        # AC - карта, PC - с кошелька
        'sum': amount,                              # сумма
        'label': label,                             # уникальная метка
        'successURL': 'https://t.me/your_bot',      # куда вернуться после оплаты
        'need-fio': 'false',
        'need-email': 'false',
        'need-phone': 'false',
        'need-address': 'false'
    }
    
    payment_url = f"https://yoomoney.ru/quickpay/confirm.xml?{urlencode(params)}"
    return payment_url, label
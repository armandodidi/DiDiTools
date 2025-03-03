import pandas as pd
import json
from tkinter import *
from tkinter import Tk, filedialog, messagebox
import re
import requests

class CreateJSON:
    @classmethod
    def get_json_base(cls, brandname):
        return {
            'auth_token': '',
            'menus': [
                {
                    'menu_name': f'Catálogo {brandname}',
                    'app_menu_id': f'Catálogo {brandname}',
                    'app_category_ids': []
                }
            ],
            'categories': [],
            'items': [],
            'merge_policy': 0
        }

    @classmethod
    def find_category(cls, categories, category_name):
        for category in categories:
            if category['category_name'] == category_name:
                return category
        return None

    @classmethod
    def trunk_string(cls, string: str, length: int):
        if len(string) > length:
            return string[:length - 3] + '...'
        return string

    @classmethod
    def replace_same_category(cls, categories, new_category):
        for category in categories:
            category['category_name'] = new_category
        return categories
    
    @classmethod
    def get_url_image(cls, image_name):
        return image_name

    @classmethod
    def run(cls, brandname, df):        
        json_base = cls.get_json_base(brandname)
        category_counter_id = 0
        product_counter = 0

        for i in range(0, len(df)):
            item_id = str(df['EAN/SKU'][i])
            price = df['PRECIO'][i]
            url = df['URL DE LA IMAGEN DEL PRODUCTO'][i]
            item_detail = {
                'activity_price': int(price)*100,
                'head_img': url,
                'app_item_id': item_id,
                'item_name': df['NOMBRE DEL PRODUCTO'][i],
                'price': int(price)*100,
                'short_desc': df['DESCRIPCIÓN'][i],
                'upc': item_id,
                'status': 1
            }
            if df['TABACO'][i] == 'Si':
                item_detail['item_tags'] = [1]
            elif df['ALCOHOL'][i] == 'Si':
                item_detail['item_tags'] = [2]
            elif df['SEXUAL'][i] == 'Si':
                item_detail['item_tags'] = [4]
            if df['ACTIVO'][i] == 'No':
                item_detail['status'] = 2
            json_base['items'].append(item_detail)
            
            category = cls.find_category(json_base['categories'], df['CATEGORIA'][i])
            if category:
                category['app_item_ids'].append(item_id)
            else:
                json_base['categories'].append({
                    'app_category_id': f'{category_counter_id}',
                    'app_item_ids': [item_id],
                    'category_name': df['CATEGORIA'][i]
                })
                json_base['menus'][0]['app_category_ids'].append(f'{category_counter_id}')
                category_counter_id += 1
            product_counter += 1
        
        print(f'jsons/{brandname}.json')
        with open(f"jsons/{brandname}.json", "w", encoding='utf-8') as outfile:
            outfile.write(json.dumps(json_base, indent=4, ensure_ascii=False))
        
        return json_base


class FormatFile:
    @classmethod
    def __itemName__(cls, df):
        df['NOMBRE DEL PRODUCTO'] = df['NOMBRE DEL PRODUCTO'].str.capitalize()
        df['NOMBRE DEL PRODUCTO'] = df['NOMBRE DEL PRODUCTO'].apply(lambda x: x if len(x) < 50 else x[:47] + '...')
        
    @classmethod
    def __description__(cls, df):
        df['DESCRIPCIÓN'] = df['DESCRIPCIÓN'].str.capitalize()
        df['DESCRIPCIÓN'] = df['DESCRIPCIÓN'].apply(lambda x: x if len(x) < 400 else x[:497] + '...')
    
    @classmethod
    def run(cls, df: pd.DataFrame) -> pd.DataFrame:
        cls.__itemName__(df)
        cls.__description__(df)
        return df

class ValidateFile:
    __errorlist__ = {}
    __haserrors__ = False
    
    @classmethod
    def __itemName__(cls, df):
        cls.__errorlist__['name_validation'] = ''
        if df['NOMBRE DEL PRODUCTO'].isnull().any():
            cls.__errorlist__['name_validation'] += '- Existen productos sin nombre.\n'

    @classmethod
    def __category__(cls, df):
        cls.__errorlist__['category_validation'] = ''
        if df['CATEGORIA'].isnull().any():
            cls.__errorlist__['category_validation'] += '- Existen productos sin categoría.\n'
    
    @classmethod
    def __price__(cls, df):
        cls.__errorlist__['price_validation'] = ''
        if df['PRECIO'].isnull().any():
            cls.__errorlist__['price_validation'] += '- Existen productos sin precio.\n'
        if (df['PRECIO'] == 0).any():
            cls.__errorlist__['price_validation'] += '- Existen productos con precio 0.\n'
    
    @classmethod
    def __stock__(cls, df):
        cls.__errorlist__['stock_validation'] = ''
        if df['STOCK'].isnull().any():
            cls.__errorlist__['stock_validation'] += '- Existen productos sin stock.\n'
        if not pd.api.types.is_integer_dtype(df['STOCK']):
            cls.__errorlist__['stock_validation'] += '- Existen con stock decimal, solo es permitido números enteros.\n'

    @classmethod
    def __imageUrl__(cls, df):
        cls.__errorlist__['image_validation'] = ''
        if df['URL DE LA IMAGEN DEL PRODUCTO'].isnull().any():
            cls.__errorlist__['image_validation'] += '- Existen productos sin imagen.\n'
        if df['URL DE LA IMAGEN DEL PRODUCTO'].str.startswith('https://drive.google.com').any():
            cls.__errorlist__['image_validation'] += '- Algunas imagenes están almacenadas en google y no será posible cargarlas.\n'
        count_invalid = (~df['URL DE LA IMAGEN DEL PRODUCTO'].str.endswith((".jpg", ".jpeg", ".webp", ".png"), na=False)).sum()
        if count_invalid > 0:
            cls.__errorlist__['image_validation'] += '- Una o más imagenes con formato incorrecto.\n'
    
    @classmethod
    def __barcodeOrSku__(cls, df):
        cls.__errorlist__['sku_validation'] = ''
        if df['EAN/SKU'].isnull().any():
            cls.__errorlist__['sku_validation'] = '- Existen productos sin código de barras o sku.\n'
        if df['EAN/SKU'].duplicated().any():
            cls.__errorlist__['sku_validation'] = '- Existen códigos de barras o skus duplicados.\n'

    @classmethod
    def run(cls, df: pd.DataFrame) -> pd.DataFrame:
        cls.__barcodeOrSku__(df)
        cls.__itemName__(df)
        cls.__category__(df)
        cls.__price__(df)
        cls.__imageUrl__(df)
        cls.__stock__(df)
        cls.__haserrors__ = (
            cls.__errorlist__['sku_validation'] 
            or cls.__errorlist__['name_validation'] 
            or cls.__errorlist__['category_validation'] 
            or cls.__errorlist__['price_validation']
            or cls.__errorlist__['stock_validation']
        )
        error_message = ''
        if cls.__errorlist__['sku_validation']:
            error_message += f'Revisar la columna EAN/SKU:\n{cls.__errorlist__['sku_validation']}\n'
        if cls.__errorlist__['name_validation']:
            error_message += f'Revisar la columna NOMBRE DEL PRODUCTO:\n{cls.__errorlist__['name_validation']}\n'
        if cls.__errorlist__['category_validation']:
            error_message += f'Revisar la columna CATEGORIA:\n{cls.__errorlist__['category_validation']}\n' 
        if cls.__errorlist__['price_validation']:
            error_message += f'Revisar la columna PRICE:\n{cls.__errorlist__['price_validation']}\n'
        if cls.__errorlist__['image_validation']:
            error_message += f'Revisar la columna IMAGE:\n{cls.__errorlist__['image_validation']}'
        if cls.__haserrors__ or cls.__errorlist__['image_validation']:
            messagebox.showerror('Errores encontrados:', error_message)
        return cls.__haserrors__

class UploadMenu:
    @classmethod
    def refreshAuthToken(cls, app_id, app_secret, app_shop_id):
        url = f'https://openapi.didi-food.com/v1/auth/authtoken/refresh?app_id={app_id}&app_secret={app_secret}&app_shop_id={app_shop_id}'
        response = requests.request('GET', url)
        return response.json()
    
    @classmethod
    def getAuthToken(cls, app_id, app_secret, app_shop_id):
        url = f'https://openapi.didi-food.com/v1/auth/authtoken/get?app_id={app_id}&app_secret={app_secret}&app_shop_id={app_shop_id}'
        response = requests.request('GET', url)
        if response.status_code == 200:
            return response.json()['data']['auth_token']
        return None
    
    @classmethod
    def uploadMenu(cls, json_menu):
        url = 'https://openapi.didi-food.com/v3/item/item/uploadGrocery'
        payload = json.dumps(json_menu, indent=4, ensure_ascii=False)
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.request('POST', url, headers=headers, data=payload)
        print(response.json())
        return response
    
    @classmethod
    def uploadStock(cls):
        pass

    @classmethod
    def run(cls, brandname, df, app_id, app_secret, app_shop_id):
        cls.refreshAuthToken(app_id, app_secret, app_shop_id)
        token = cls.getAuthToken(app_id, app_secret, app_shop_id)
        if not token:
            raise ValueError(f'Error al obtener el token de la tienda: {app_shop_id}')
        json_menu = CreateJSON.run(brandname, df)
        json_menu['auth_token'] = token
        cls.uploadMenu(json_menu)

class UploadMenuAndStock:
    @classmethod
    def choose_menu_file(cls):
        # Ocultar la ventana principal de Tkinter
        root = Tk()

        # Pedir al usuario que seleccione el primer archivo Excel
        archivo = filedialog.askopenfilename(
            title='Selecciona el menú a cargar:',
            filetypes=[('Archivos Excel', '*.xlsx *.xls')]
        )

        try:
            return archivo, root
        except Exception as e:
            messagebox.showerror('Error', f'Error al leer los archivos Excel: {e}')
            return
        
    @classmethod
    def get_app_credentials(cls, tk_root):
        tk_root.title('Credenciales de la aplicación')
        tk_root.geometry('300x300')
        
        # Variables para almacenar los valores de los campos
        app_id_var = StringVar(value="5764607640045355814")
        app_secret_var = StringVar(value="2c3fcc0094e5fdc5efe44fb2bdd4a007")
        shop_id_var = StringVar(value="404")
        
        def submit_form():
            nonlocal submitted_values
            submitted_values = {
                "app_id": app_id_var.get(),
                "app_secret": app_secret_var.get(),
                "app_shop_id": shop_id_var.get(),
            }
            tk_root.destroy()  # Cerrar ventana
        
        submitted_values = {}        
        # Create labels and entry fields for each input
        Label(tk_root, text='App ID:').pack(pady=5)
        Entry(tk_root, textvariable=app_id_var).pack()

        Label(tk_root, text='App secret:').pack(pady=5)
        Entry(tk_root, textvariable=app_secret_var).pack()

        Label(tk_root, text='Shop IDs:').pack(pady=5)
        Entry(tk_root, textvariable=shop_id_var).pack()
        
        Button(tk_root, text='Register', command=submit_form).pack(pady=5)
        
        tk_root.mainloop()
        
        # Get the user input from the form
        return submitted_values

    @classmethod
    def get_brand_name(cls, file_path):
        return re.search(r'([^/]+)(?=\.xlsx)', file_path).group()
    
    @classmethod
    def upload_menu(cls, brandname, df, tk_root):
        app_credentials = cls.get_app_credentials(tk_root)
        UploadMenu.run(brandname, df, **app_credentials)

    @classmethod
    def run(cls):
        file_path, tk_root = cls.choose_menu_file()
        brandname = cls.get_brand_name(file_path)
        df = pd.read_excel(file_path)
        try:
            messagebox.showinfo('Verificando', '     Validando menú...     ')
            if ValidateFile.run(df):
                messagebox.showerror('Errores', '     Existen errores en      ')
                return
            df = FormatFile.run(df)
            # df.to_excel(file_path)
            messagebox.showinfo('Validación éxitosa', '     Validación éxitosa     ')
            messagebox.showinfo('Carga de datos', '     Ingresa la información para carga menú a las tiendas     ')
            cls.upload_menu(brandname, df, tk_root)
            messagebox.showinfo('Proceso de carga éxitoso', 'Archivos procesados y subidos exitosamente.')
        except Exception as e:
            messagebox.showerror('Error', f'     Ha ocurrido un error: {e}     ')

# Execute propgram
if __name__ == "__main__":
    UploadMenuAndStock.run()

# System_sgq
> A fullstack application for roofing budget, including polycarbonate and isothermal tile, this is a small version of a full deployed application that i developed.

### :mag_right: Some observations
- The logos of the company are hidden for legal purposes. I will create some logos in the future for this repository.
- The system was written in brazilian portuguese :brazil:.

### :wrench: Built With
- Django
- Mysql
- Alot of ajax requests

---
## 🚀 Getting Started

### Requirements
- Mysql
- Python >= 3.7
- Pip

### Instalation
1. Clone this repo to your local machine
```sh
  git clone https://github.com/luizhenriquemaia/system_sgq.git
 ```
2. Install the requirements.txt 
 ```sh
   pip install -r requirements.txt
   ```
> Observation: the installation of mysqlclient usually doesn't work if you install direct using pip, so use a wheel file and edit the requirements file to match to the path of the file.
> You can find the wheel packages in `https://pypi.org/project/mysqlclient/#files`

### First configurations
1. Create a database in mysql
2. Create in the root directory a file called access_db.txt and inside the file write the name of your database, the user and finally the password using lines as separator
3. Create in the root directory a file called secret_key.txt
4. Obtain a secret from <a href="https://miniwebtool.com/django-secret-key-generator/" target="_blank">**MiniWebTool**</a> key and add to secret_key.txt
5. Create a .gitignore file and add access_db.txt and secret_key.txt
6. Migrate
```sh
  python manage.py migrate
```
7. Create a superuser
```sh
  python manage.py createsuperuser
```
8. Make the migratiosn
```sh
  python manage.py makemigrations
```
9. Migrate
```sh
  python manage.py migrate
```
10. Run the server
```sh
  python manage.py runserver
```
## :page_facing_up: Adding essential data in the system
### Adding seeds to system
> This part is necessary because of the relations ships between the tables
1. Login with your superuser account while the server are runing
2. Inside the `http://127.0.0.1:8000/apps-disponiveis/` go to `Configurações` > `Adicionar dados essenciais no banco de dados`
3. Click in each of the items of the list 

### Adding a company and cost center
> This part is necessary because this is a system to work with more than 1 type of budget, so each company can have his own budgets and each company can have alot of cost centers
1. Inside the `http://127.0.0.1:8000/config/` go to `Empresas` and add data of the company
2. Click the new company id and add a cost center
---

## :computer: Usage
> In this repository i only put the first app `Gerenciamento Comercial` where you can make budgets
- Click in `Novo Orçamento` on navigation bar
- Add a new client information
- Select the company and cost center
- Add a new service to the budget or a new eap manually to the budget
> If you add manually you have to add each input of the budget one by one
- Click in show details of a external delivery to see the inputs
- After add all the external deliverys and totalizers click in sandwich menu in bottom right and click in `Gerar Proposta`
- Edit the data and print as pdf the price proposal

---
## 📝 License
- Distributed under the MIT License.
---

## 🤝 Team

> Or Contributors/People

| <a href="https://github.com/luizhenriquemaia" target="_blank">**Luiz Henrique**</a> |
|:---:|
| ![Luiz Henrique](https://avatars1.githubusercontent.com/u/26177048?s=200&u=1deb4b3947a75f8baca3123f6a23e8a803f53493&v=4) |
| <a href="https://github.com/luizhenriquemaia" target="_blank">`github.com/luizhenriquemaia`</a> |






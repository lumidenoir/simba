# SIMBA (Simple Inventory Management and Billing Application)

SIMBA is a lightweight inventory management and billing system designed for seamless operation. Built using Django, it supports billing with PDF generation via WeasyPrint and offers features tailored to ease inventory and sales management.

## Features

1. **Item Management**
   - Add items which can be edited and deleted
   - Track stock levels and automatically generate restocking suggestions based on total sales.

2. **Purchaser Types**
   - Different purchaser categories for tailored pricing and tracking (retailer, chef and bulk).

3. **Sales Management** 
   - Apply individual discounts during the sale.
   - Generate itemized bills stored locally as PDFs in the `bills` subfolder.
   - View and filter previous sales.
   - Handle returns on purchases made within the last 7 days.

4. **Reports** 
   - Identify items that need restocking, sorted by total sales.
   - Sales analysis charts (Work in Progress).

## Installation 

1. **Clone the Repository**
   ```bash
   git clone https://github.com/lumidenoir/simba.git
   cd simba
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   or if you use poetry
   ```bash
   poetry install --no-root
   ```

3. **Set Up the Database**
   ```bash
   python manage.py migrate
   ```

4. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```
   or with poetry run
   ```bash
   poetry run python manage.py runserver
   ```

## Usage

- Create a superuser with `python manage.py createsuperuser`
- Create an user id at `http://127.0.0.1:8000/admin`.
- Access the application at `http://127.0.0.1:8000/`.
- Add items and manage inventory via the admin panel or UI.
- Process sales and generate bills with individual item discounts.
- Use the "View Sales" section to manage refunds for eligible purchases.
- View restocking view to ensure stock availability.


## Local PDF Storage

- All generated bills are saved as PDFs in the `bill/` folder.
- Easily access or print past bills from the storage.


## Future Enhancements

- Integration of sales analysis charts.
- Enhanced reporting features for business insights.


## Contributing

- Fork the repository and submit a pull request for new features or bug fixes.
- For major changes, open an issue to discuss your ideas.

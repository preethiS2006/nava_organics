# Nava Organics – Pure Herbal Essentials

Simple, modern ecommerce demo for herbal products built with a clean Flask stack, SQLite storage, and minimal frontend.

**Tech Stack**
- Flask · Flask-SQLAlchemy · SQLAlchemy · SQLite · Jinja2 · HTML · CSS · JavaScript · Python

**Key Features**
- Product catalog, search, and details
- Cart, checkout, and order creation
- Payment simulation with success tick and receipt page
- Order timeline: Placed → Confirmed → Dispatched → Reached
- Admin management for products, offers, and orders (gated in sequence)
- My Orders page for users with tracking and receipt links
- Favourites with add/remove
- Updated contact and Instagram link in footer

## Getting Started

```powershell
# from project root
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# initialize database and seed sample data (products/offers/admin)
flask --app app.py init-db

# run dev server
flask --app app.py run
```

Open `http://127.0.0.1:5000/` in your browser.

## Admin Access

- Email: `admin@navaorganics.test`
- Password: `admin123`

Admin can update statuses in order: `Order Placed` → `Order Confirmed` → `Order Dispatched`. The final step `Order Reached` is marked by the user from their tracking page. Admin cannot add to cart or checkout.

## Project Structure

- `app.py` – Flask app, models, routes
- `templates/` – Jinja2 templates (pages, admin views)
- `static/css/styles.css` – Base styles and components
- `static/js/main.js` – Small frontend helpers
- `nava_organics.db` – SQLite database (created after init)

## Common Commands

- Initialize DB and seed: `flask --app app.py init-db`
- Run server: `flask --app app.py run`

## Troubleshooting

- If you encounter a missing-table error, re-initialize the database: `flask --app app.py init-db`
- On Windows, activate the virtual environment with: `. .venv\Scripts\Activate.ps1`

## License

For demo and educational use.

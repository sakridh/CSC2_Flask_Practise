from flask import Flask, render_template, request, session, flash, redirect, url_for
import json
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'


def load_data():
    with open("data/flowers.json") as file:
        flowers = json.load(file)
    with open("data/addons.json") as file:
        addons = json.load(file)
    return flowers, addons


def calculate_total(cart, selected_addons):
    flower_subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    addon_subtotal = sum(selected_addons.values())
    total = flower_subtotal + addon_subtotal
    return total, flower_subtotal, addon_subtotal


@app.route("/")
def home():
    flowers, addons = load_data()
    selected_addons = session.get("selected_addons", {})
    cart = session.get('cart', {})
    total, flower_subtotal, addon_subtotal = calculate_total(cart, selected_addons)

    # Optional: highlight expensive orders (Slide 15)
    if total > 100:
        flash("You are ordering a lot! Consider calling us for a special deal.")

    return render_template(
        "index.html",
        flowers=flowers,
        addons=addons,
        cart=cart,
        total=total,
        flower_subtotal=flower_subtotal,
        addon_subtotal=addon_subtotal,
        selected_addons=selected_addons
    )


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    flower = request.form['flower']
    quantity = int(request.form['quantity'])
    flowers, addons = load_data()
    cart = session.get('cart', {})

    if flower not in flowers:
        flash("Invalid flower selected.")
        return redirect(url_for('home'))

    if flower in cart:
        cart[flower]['quantity'] += quantity
    else:
        cart[flower] = {
            'price': flowers[flower]['price'],
            'quantity': quantity
        }

    session['cart'] = cart
    session.modified = True
    flash(f"{quantity} {flower}(s) added to cart.")
    return redirect(url_for('home'))


@app.route("/select_addon", methods=["POST"])
def select_addon():
    selected_addons = {}
    _, addons = load_data()
    selected_keys = request.form.getlist("addons")

    for addon in selected_keys:
        if addon in addons:
            selected_addons[addon] = float(addons[addon]['price'])

    session['selected_addons'] = selected_addons
    session.modified = True

    if selected_addons:
        flash(f"{len(selected_addons)} add-on(s) added to cart.")
    else:
        flash("No add-ons selected.")

    return redirect(url_for('home'))


@app.route('/remove_from_cart/<item>')
def remove_from_cart(item):
    cart = session.get('cart', {})
    if item in cart:
        del cart[item]
        session['cart'] = cart
        session.modified = True
        flash(f"Removed all {item.capitalize()} from the cart.")
    else:
        flash("Item not found in cart.")
    return redirect(url_for('home'))


@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    session.pop('cart', None)
    session.pop('selected_addons', None)
    session.modified = True
    flash("Order cancelled. Your cart has been emptied.")
    return redirect(url_for('home'))


@app.route('/checkout', methods=['POST'])
def checkout():
    customer_name = request.form['customer_name'].strip().title()

    if not customer_name:
        flash("Customer name is required.")
        return redirect(url_for('home'))

    cart = session.get('cart', {})
    selected_addons = session.get('selected_addons', {})

    if not cart:
        flash("Your cart is empty.")
        return redirect(url_for('home'))

    total, flower_subtotal, addon_subtotal = calculate_total(cart, selected_addons)

    invoice_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    invoice_number = f"INV_{customer_name.replace(' ', '_')}_{invoice_date}"

    # Clear session after checkout
    session.pop('cart', None)
    session.pop('selected_addons', None)
    session.modified = True

    return render_template(
        'invoice.html',
        customer_name=customer_name,
        cart=cart,
        selected_addons=selected_addons,
        total=total,
        flower_subtotal=flower_subtotal,
        addon_subtotal=addon_subtotal,
        invoice_date=invoice_date,
        invoice_number=invoice_number
    )


if __name__ == "__main__":
    app.run(debug=True)
import markdown
from flask import Flask, render_template, request, redirect, jsonify, flash
from collections import defaultdict
import pickle
from datetime import datetime
import os
import re
import pytz
from werkzeug.security import check_password_hash, generate_password_hash
import subprocess

users_file = 'users.pkl'
product_file = 'product.pkl'
location_file = 'location.pkl'
movement_file = 'movement.pkl'
counter_file = 'counter.txt'  # File for creating IDs

if not os.path.exists('users.pkl'):
    # Create the file if it doesn't exist
    open('users.pkl', 'wb').close()

if not os.path.exists('movement.pkl'):
    open('movement.pkl', 'wb').close()

if not os.path.exists('product.pkl'):
    open('product.pkl', 'wb').close()

if not os.path.exists('location.pkl'):
    open('location.pkl', 'wb').close()

if not os.path.exists('counter.txt'):
    open('counter.txt', 'wb').close()

app = Flask(__name__)
app.secret_key = 'gJwlRqBv959595'


# Remove customer and remove location when display options to add a new movement
def remove_specific_locations(locations, names_to_remove):
    return [location for location in locations if location.location_id not in names_to_remove]


# Read ID counter
def read_counter(filename):
    try:
        with open(filename, 'r') as file:
            counter = int(file.read())
    except FileNotFoundError:
        # If the file doesn't exist, start with counter value 0
        counter = 0
    return counter


# Save ID counter
def write_counter(filename, counter):
    with open(filename, 'w') as file:
        file.write(str(counter))


def save_to_pkl(data, filename):
    with open(filename, 'wb') as file:
        pickle.dump(data, file)


def load_from_pkl(filename):
    try:
        with open(filename, 'rb') as file:
            return pickle.load(file)
    except EOFError:
        return []


class Product:
    def __init__(self, product_id, price, purchase_price):
        self.product_id = product_id
        self.date_created = datetime.now().astimezone(pytz.timezone('America/New_York')).strftime("%A, %B %d, %Y "
                                                                                                  "%I:%M %p")
        self.price = price
        self.purchase_price = purchase_price

    def __repr__(self):
        return f'<Product {self.product_id}>'


class Location:
    def __init__(self, location_id):
        self.location_id = location_id
        self.date_created = datetime.now().astimezone(pytz.timezone('America/New_York')).strftime("%A, %B %d, %Y "
                                                                                                  "%I:%M %p")

    def __repr__(self):
        return f'<Location {self.location_id}>'


class Movement:
    def __init__(self, price, movement_id, product_id, qty, from_location, to_location):
        self.price = price
        self.movement_id = movement_id
        self.product_id = product_id
        self.qty = qty
        self.from_location = from_location
        self.to_location = to_location
        self.movement_time = datetime.now().astimezone(pytz.timezone('America/New_York')).strftime("%A, %B %d, %Y "
                                                                                                   "%I:%M %p")

    def __repr__(self):
        return f'<Movement {self.movement_id}>'


@app.route('/', methods=['GET', 'POST'])
def login_register():
    if request.method == 'POST':
        form_type = request.form['form_type']
        if form_type == 'login':
            username_or_email = request.form['username_or_email']
            password = request.form['password']
            users = load_from_pkl(users_file)
            user = next((u for u in users if u['username'] == username_or_email or u['email'] == username_or_email),
                        None)

            if user and check_password_hash(user['password'], password):
                flash('Login successful')
                return redirect('/home')
            else:
                flash('Invalid username/email or password')
        elif form_type == 'register':
            name = request.form['name']
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            users = load_from_pkl(users_file)

            if any(u['username'] == username for u in users):
                flash('Username already exists')
            elif any(u['email'] == email for u in users):
                flash('Email already exists')
            else:
                hashed_password = generate_password_hash(password)
                users.append({'name': name, 'username': username, 'email': email, 'password': hashed_password})
                save_to_pkl(users, users_file)
                flash('Registration successful. Please login.')
                return redirect('/')

    return render_template('login.html')


@app.route('/home', methods=["POST", "GET"])
def index():
    # add new product
    if (request.method == "POST") and ('product_name' in request.form):
        product_name = request.form["product_name"]
        new_product = Product(product_id=product_name)

        try:
            products = load_from_pkl(product_file)
            products.append(new_product)
            save_to_pkl(products, product_file)
            return redirect("/home")

        except Exception as e:
            return f"There Was an issue while add a new Product + {e}"

    # add new location
    if (request.method == "POST") and ('location_name' in request.form):
        location_name = request.form["location_name"]
        new_location = Location(location_id=location_name)

        try:
            locations = load_from_pkl(location_file)
            locations.append(new_location)
            save_to_pkl(locations, location_file)
            return redirect("/home")

        except Exception as e:
            return f"There Was an issue while add a new Location + {e}"
    else:
        return render_template("index.html", products=load_from_pkl(product_file),
                               locations=load_from_pkl(location_file))


@app.route('/chat/', methods=["POST", "GET"])
def chat():
    user_input = request.form.get('enter_chat')

    if user_input:
        try:
            # Construct the shell command (ollama and phi3 must be installed on hosting server)
            shell_command = f"echo {user_input} | /usr/local/bin/ollama run phi3"

            # Execute the shell command
            process = subprocess.Popen(shell_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()

            # Kill Ollama server
            subprocess.Popen("pkill -f ollama", shell=True)
            subprocess.Popen("pkill -f Ollama", shell=True)

            # Get the response
            response = stdout.decode('utf-8') if stdout else stderr.decode('utf-8')
            response = re.sub(r'\n', '', response)
        except Exception as e:
            response = str(e)
    else:
        response = "No input provided"

    return render_template("index.html", response=response)


@app.route('/locations/', methods=["POST", "GET"])
def viewLocation():
    if (request.method == "POST") and ('location_name' in request.form):
        location_name = request.form["location_name"]
        new_location = Location(location_id=location_name)

        try:
            locations = load_from_pkl(location_file)
            locations.append(new_location)
            save_to_pkl(locations, location_file)
            return redirect("/locations/")

        except Exception:
            locations = load_from_pkl(location_file)
            return render_template("locations.html", locations=locations)
    else:
        locations = load_from_pkl(location_file)
        return render_template("locations.html", locations=locations)


@app.route('/products/', methods=["POST", "GET"])
def viewProduct():
    if (request.method == "POST") and ('product_name' in request.form):
        product_name = request.form["product_name"]
        product_price = request.form["product_price"]
        purchase_price = request.form["purchase_price"]
        new_product = Product(product_id=product_name, price=product_price, purchase_price=purchase_price)

        try:
            products = load_from_pkl(product_file)
            products.append(new_product)
            save_to_pkl(products, product_file)
            return redirect("/products/")

        except Exception:
            return "There Was an issue while add a new Product"
    else:
        products = load_from_pkl(product_file)
        return render_template("products.html", products=products)


@app.route("/update-product/<name>", methods=["POST", "GET"])
def updateProduct(name):
    products = load_from_pkl(product_file)
    product = next((prod for prod in products if prod.product_id == name), None)

    if not product:
        return "Product not found", 404

    old_product_id = product.product_id
    if request.method == "POST":
        new_product_id = request.form['product_name']
        new_price = request.form['product_price']
        new_purchase_price = request.form['purchase_price']
        product.product_id = new_product_id
        product.price = new_price
        product.purchase_price = new_purchase_price

        try:
            save_to_pkl(products, product_file)
            updateProductInMovements(old_product_id, new_product_id)
            return redirect("/products/")
        except Exception as e:
            return f"There was an issue while updating the Product: {str(e)}"
    else:
        return render_template("update-product.html", product=product, price=product.price,
                               purhcase_price=product.purchase_price)


@app.route("/delete-product/<name>")
def deleteProduct(name):
    """Deletes a product by removing it from the pickle file."""
    try:
        products = load_from_pkl(product_file)
        product_to_delete = next((prod for prod in products if prod.product_id == name), None)

        if not product_to_delete:
            return "Product not found", 404

        products.remove(product_to_delete)
        save_to_pkl(products, product_file)
        return redirect("/products/")
    except Exception as e:
        return f"There was an issue while deleting the Product: {str(e)}"


@app.route("/update-location/<name>", methods=["POST", "GET"])
def updateLocation(name):
    """Updates a location by modifying the pickle file."""
    try:
        locations = load_from_pkl(location_file)
        location = next((loc for loc in locations if loc.location_id == name), None)

        if not location:
            return "Location not found", 404

        old_location = location.location_id
        # Handles updating location
        if request.method == "POST":
            location.location_id = request.form['location_name']

            try:
                save_to_pkl(locations, location_file)
                updateLocationInMovements(old_location, request.form['location_name'])
                return redirect("/locations/")
            except Exception as e:
                return f"There was an issue while updating the Location: {str(e)}"
        else:
            return render_template("update-location.html", location=location)
    except Exception as e:
        return f"There was an issue while loading the Location: {str(e)}"


@app.route("/delete-location/<name>")
def deleteLocation(name):
    try:
        locations = load_from_pkl(location_file)
        location_to_delete = next((loc for loc in locations if loc.location_id == name), None)

        if not location_to_delete:
            return "Location not found", 404

        locations.remove(location_to_delete)
        save_to_pkl(locations, location_file)
        return redirect("/locations/")
    except Exception as e:
        return f"There was an issue while deleting the Location: {str(e)}"


@app.route("/movements/", methods=["POST", "GET"])
def viewMovements():
    global price
    products = load_from_pkl(product_file)
    # Handles adding new movement
    if request.method == "POST":
        product_id = request.form["productId"]
        for product in products:
            if product_id == product.product_id:
                price = product.price
        qty = request.form["qty"]
        fromLocation = request.form["fromLocation"]
        toLocation = request.form["toLocation"]
        # gets ID from file and increments it
        counter = read_counter(counter_file)
        counter += 1
        new_movement = Movement(
            price=price,
            movement_id=counter,
            product_id=product_id,
            qty=qty,
            from_location=fromLocation,
            to_location=toLocation
        )
        write_counter(counter_file, counter)
        try:
            movements = load_from_pkl(movement_file)
            movements.append(new_movement)
            save_to_pkl(movements, movement_file)
            return redirect("/movements/")
        except Exception as e:
            return f"There was an issue while adding a new Movement: {str(e)}"
    else:
        products = load_from_pkl(product_file)
        movements = load_from_pkl(movement_file)
        return render_template("movements.html", movements=movements, products=products,
                               locations=remove_specific_locations(load_from_pkl(location_file), ["Customer"]))


@app.route("/update-movement/<int:id>", methods=["POST", "GET"])
def updateMovement(id):
    try:
        movements = load_from_pkl(movement_file)
        movement = next((mov for mov in movements if int(mov.movement_id) == id), None)
        if not movement:
            return "Movement not found", 404

        products = load_from_pkl(product_file)
        product = next((pro for pro in products), None)
        locations = load_from_pkl(location_file)

        if request.method == "POST":
            movement.price = product.price
            movement.product_id = request.form["productId"]
            movement.qty = int(request.form["qty"])
            movement.from_location = request.form["fromLocation"]
            movement.to_location = request.form["toLocation"]

            try:
                save_to_pkl(movements, movement_file)
                return redirect("/movements/")
            except Exception as e:
                return f"There was an issue while updating the Product Movement: {str(e)}"
        else:
            return render_template("update-movement.html", movement=movement, locations=locations, products=products)
    except Exception as e:
        return f"There was an issue while loading the data: {str(e)}"


@app.route("/delete-movement/<int:id>")
def deleteMovement(id):
    try:
        movements = load_from_pkl(movement_file)
        movement_to_delete = next((mov for mov in movements if int(mov.movement_id) == id), None)

        if not movement_to_delete:
            return "Movement not found", 404

        movements.remove(movement_to_delete)
        save_to_pkl(movements, movement_file)
        return redirect("/movements/")
    except Exception as e:
        return f"There was an issue while deleting the Product Movement: {str(e)}"


@app.route("/product-balance/", methods=["POST", "GET"])
def productBalanceReport():
    """Shows current inventory"""
    try:
        movements = load_from_pkl(movement_file)

        balancedDict = defaultdict(lambda: defaultdict(dict))
        tempProduct = ''

        for mov in movements:
            if tempProduct == mov.product_id:
                if not (not mov.to_location or "qty" in balancedDict[mov.product_id][mov.to_location]):
                    balancedDict[mov.product_id][mov.to_location]["qty"] = 0
                if not (not mov.from_location or "qty" in balancedDict[mov.product_id][mov.from_location]):
                    balancedDict[mov.product_id][mov.from_location]["qty"] = 0

                # Ensure mov.qty is an integer
                qty_to_add = int(mov.qty)

                if mov.to_location and "qty" in balancedDict[mov.product_id][mov.to_location]:
                    balancedDict[mov.product_id][mov.to_location]["qty"] = int(
                        balancedDict[mov.product_id][mov.to_location]["qty"]) + qty_to_add

                if mov.from_location and "qty" in balancedDict[mov.product_id][mov.from_location]:
                    balancedDict[mov.product_id][mov.from_location]["qty"] = int(
                        balancedDict[mov.product_id][mov.from_location]["qty"]) - qty_to_add
            else:
                tempProduct = mov.product_id
                if mov.to_location and not mov.from_location:
                    balancedDict[mov.product_id][mov.to_location]["qty"] = mov.qty

        return render_template("product-balance.html", movements=balancedDict)
    except Exception as e:
        return f"There was an issue while loading the data: {str(e)}"


@app.route("/revenue-report/", methods=["POST", "GET"])
def revenueReport():
    movements = load_from_pkl(movement_file)
    products = load_from_pkl(product_file)
    revenue = 0
    products_dict = {}
    for mov in movements:
        if mov.to_location == 'Customer':
            for product in products:
                if mov.product_id == product.product_id:  # Checks if product was bought by customer
                    products_dict[product] = mov.qty
                    revenue += (float(product.price) - float(product.purchase_price)) * int(mov.qty)
    return render_template("revenue-report.html", revenue_data="{:.2f}".format(revenue), products=products_dict)


@app.route("/movements/get-from-locations", methods=["POST"])
def getLocations():
    product = request.form["productId"]
    locationDict = defaultdict(int)  # Use a single dictionary for quantities

    movements = load_from_pkl(movement_file)
    for mov in movements:
        if mov.product_id == product:
            locationDict[mov.from_location] += mov.qty

    # Filter out "Customer" and "remove"
    filtered_locations = {loc: qty for loc, qty in locationDict.items() if loc not in ["Customer", "Remove"]}
    return filtered_locations


@app.route("/dup-locations/", methods=["POST", "GET"])
def getDuplicate():
    """Checks if there are any duplicate locations for input handling when updating location"""
    location = request.form["location"]
    locations = load_from_pkl(location_file)
    if len(location) == 0:
        return {"output": False}
    duplicate = any(loc.location_id == location for loc in locations)

    return {"output": not duplicate}


def is_valid_price(price):
    """Checks if the price is valid for input validation when updating the product"""
    # Define the price pattern using a regular expression
    price_pattern = re.compile(r'^\d+\.\d{2}$')

    # Check if the price matches the pattern
    if price_pattern.match(price):
        return True
    else:
        return False


@app.route("/dup-products/", methods=["POST", "GET"])
def getPDuplicate():
    """Checks if there are any duplicate product names when updating product as input validation"""
    product_name = request.form["product_name"]
    product_price = request.form["product_price"]
    purchase_price = request.form["purchase_price"]
    products = load_from_pkl(product_file)
    duplicate = any(prod.product_id == product_name for prod in products)

    return {"output": ((not duplicate) and is_valid_price(product_price) and is_valid_price(purchase_price))}


@app.route("/cart", methods=["POST", "GET"])
def cart():
    movements = load_from_pkl(movement_file)
    # Filter movements to include only unique product names
    unique_movements = {}
    for movement in movements:
        if movement.product_id not in unique_movements:
            unique_movements[movement.product_id] = movement

    return render_template("cart.html", movements=unique_movements.values())  # Sends add to cart page


@app.route('/checkout', methods=['POST'])
def checkout():
    """Changes the inventory depending on what the user bought (receipt printing functionality is in html file)"""
    try:
        data = request.json
        movements_data = data['movements']
        movements = load_from_pkl(movement_file)
        locations = load_from_pkl(location_file)
        customer_location = next((loc for loc in locations if loc.location_id == 'Customer'), None)
        if not customer_location:
            customer_location = Location(location_id='Customer')
            locations.append(customer_location)
            save_to_pkl(locations, location_file)

        for mov_data in movements_data:
            product_id = mov_data['productId']
            qty = int(mov_data['quantity'])

            # Find the movement with the largest quantity for this product
            from_movement = max(
                (m for m in movements if m.product_id == product_id and m.to_location != 'Customer'),
                key=lambda m: m.qty,
                default=None
            )

            if from_movement:
                counter = read_counter(counter_file)
                counter += 1
                new_movement = Movement(
                    price=from_movement.price,
                    movement_id=counter,
                    product_id=product_id,
                    qty=qty,
                    from_location=from_movement.to_location,
                    to_location='Customer'
                )
                write_counter(counter_file, counter)
                movements.append(new_movement)

                # Update the original movement's quantity
                from_movement.qty = int(from_movement.qty) - qty  # Convert qty to integer before subtraction
                if from_movement.qty <= 0:
                    movements.remove(from_movement)
                else:
                    from_movement.qty = str(from_movement.qty)  # Convert back to string if needed

        save_to_pkl(movements, movement_file)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def updateLocationInMovements(old_location, new_location):
    """When a location is changed, it needs to be updated in movements that happened before the location was changed"""
    movements = load_from_pkl(movement_file)

    for mov in movements:
        if mov.from_location == old_location:
            mov.from_location = new_location
        if mov.to_location == old_location:
            mov.to_location = new_location

    save_to_pkl(movements, movement_file)


def updateProductInMovements(old_product, new_product):
    """When a product name is changed, it needs to be updated in movements that happened before the product name was
    changed"""
    try:
        movements = load_from_pkl(movement_file)
        for mov in movements:
            if mov.product_id == old_product:
                mov.product_id = new_product
        save_to_pkl(movements, movement_file)
    except Exception as e:
        return f"There was an issue while updating the Product in Movements: {str(e)}"


if __name__ == "__main__":
    # Create a customer 'location'
    locations = load_from_pkl(location_file)
    if 'Customer' not in [loc.location_id for loc in locations]:
        customer = Location(location_id='Customer')  # Customer is treated as a location
        locations.append(customer)
    if 'Remove' not in [loc.location_id for loc in locations]:
        remove = Location(location_id='Remove')  # Option to remove inventory
        locations.append(remove)
    save_to_pkl(locations, location_file)
    app.run(debug=True)

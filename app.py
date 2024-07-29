from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://myuser:mypass@localhost/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    precio = db.Column(db.Integer, nullable=False)
    imagen = db.Column(db.String(100), nullable=False)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    usuario = db.relationship('Usuario', backref=db.backref('carts', lazy=True))
    producto = db.relationship('Producto', backref=db.backref('carts', lazy=True))

# Crear las tablas si no existen
with app.app_context():
    db.create_all()

def agregar_producto(nombre, categoria, precio, imagen):
    if Producto.query.filter_by(nombre=nombre).first():
        print(f"El producto '{nombre}' ya existe en la base de datos.")
        return
    try:
        nuevo_producto = Producto(nombre=nombre, categoria=categoria, precio=precio, imagen=imagen)
        db.session.add(nuevo_producto)
        db.session.commit()
        print(f"Producto agregado: {nombre}")
    except Exception as e:
        print(f"Error al agregar producto: {e}")
        db.session.rollback()

def eliminar_producto(product_id):
    producto = Producto.query.get(product_id)
    if producto:
        try:
            db.session.delete(producto)
            db.session.commit()
            print(f'Producto "{producto.nombre}" eliminado exitosamente.')
        except Exception as e:
            db.session.rollback()
            print(f'Error al eliminar el producto: {e}')
    else:
        print('El producto no existe.')

def actualizar_producto(product_id, nuevo_nombre=None, nueva_categoria=None, nuevo_precio=None, nueva_imagen=None):
    producto = Producto.query.get(product_id)
    if producto:
        if nuevo_nombre:
            producto.nombre = nuevo_nombre
        if nueva_categoria:
            producto.categoria = nueva_categoria
        if nuevo_precio is not None:
            producto.precio = nuevo_precio
        if nueva_imagen:
            producto.imagen = nueva_imagen
        try:
            db.session.commit()
            print(f'Producto "{producto.nombre}" actualizado exitosamente.')
        except Exception as e:
            db.session.rollback()
            print(f'Error al actualizar el producto: {e}')
    else:
        print('El producto no existe.')

# Función para agregar productos iniciales solo si están vacíos
def agregar_productos_iniciales():
    if not Producto.query.first():
        productos_a_agregar = [
            {'nombre': 'Televisor Samsung 56 pulgadas Full Hd', 'categoria': 'Categoria 1', 'precio': 350000, 'imagen': 'televisor.jpg'},
            {'nombre': 'Sony Playstation 5 1 TB', 'categoria': 'Categoria 1', 'precio': 800000, 'imagen': 'play.jpg'},
            {'nombre': 'Monitor Samsung 24 pulgadas 75hs', 'categoria': 'Categoria 1', 'precio': 120000, 'imagen': 'monitor.jpg'},
            {'nombre': 'Macbook Pro m3', 'categoria': 'Categoria 2', 'precio': 4000000, 'imagen': 'macbook.jpg'},
            {'nombre': 'Iphone 15 Pro Max 256gb', 'categoria': 'Categoria 2', 'precio': 1500000, 'imagen': 'iphone.jpg'},
            {'nombre': 'Airpods 3', 'categoria': 'Categoria 2', 'precio': 150000, 'imagen': 'airpods.jpg'},
            {'nombre': 'Airpods Max', 'categoria': 'Categoria 3', 'precio': 300000, 'imagen': 'airpodsmax.jpg'},
            {'nombre': 'Aire acondicionado Whirpool frio/calor', 'categoria': 'Categoria 3', 'precio': 450000, 'imagen': 'aire.jpg'},
            {'nombre': 'Heladera Samsung Pro', 'categoria': 'Categoria 3', 'precio': 999999, 'imagen': 'heladera.jpg'}
            
        ]
        for producto in productos_a_agregar:
            agregar_producto(producto['nombre'], producto['categoria'], producto['precio'], producto['imagen'])

@app.route('/')
def index():
    productos = Producto.query.all()
    return render_template('index.html', productos=productos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        usuario = Usuario.query.filter_by(username=username, password=password).first()
        if usuario:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Usuario inexistente o contraseña incorrecta. Vuelve a intentarlo o cambia la contraseña', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        
        if len(username) < 5:
            flash('El nombre de usuario debe tener al menos 5 caracteres', 'error')
        elif len(password) < 5:
            flash('La contraseña debe tener al menos 5 caracteres', 'error')
        elif not Usuario.query.filter_by(username=username).first():
            usuario = Usuario(username=username, password=password)
            db.session.add(usuario)
            db.session.commit()
            session['username'] = username
           
            return redirect(url_for('index'))
        else:
            flash('Este usuario ya existe', 'error')
    return render_template('register.html')

@app.route('/cambiar_contrasena', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username'].lower()
        new_password = request.form['new_password']
        
        usuario = Usuario.query.filter_by(username=username).first()
        if usuario:
            if len(new_password) >= 5:
                usuario.password = new_password
                db.session.commit()
                flash('Contraseña actualizada exitosamente. Puedes iniciar sesión con tu nueva contraseña.', 'success')
                return redirect(url_for('login'))
            else:
                flash('La nueva contraseña debe tener al menos 5 caracteres', 'error')
        else:
            flash('El nombre de usuario no existe', 'error')
    
    return render_template('cambiar_contrasena.html')


@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'username' in session:
        username = session['username']
        usuario = Usuario.query.filter_by(username=username).first()
        if usuario:
            cart_item = Cart(user_id=usuario.id, product_id=product_id)
            db.session.add(cart_item)
            db.session.commit()
    return redirect(url_for('index'))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'username' in session:
        username = session['username']
        usuario = Usuario.query.filter_by(username=username).first()
        if usuario:
            cart_item = Cart.query.filter_by(user_id=usuario.id, product_id=product_id).first()
            if cart_item:
                db.session.delete(cart_item)
                db.session.commit()
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart_products = []
    total = 0
    if 'username' in session:
        username = session['username']
        usuario = Usuario.query.filter_by(username=username).first()
        if usuario:
            cart_items = Cart.query.filter_by(user_id=usuario.id).all()
            for item in cart_items:
                producto = Producto.query.get(item.product_id)
                if producto:
                    cart_products.append(producto)
                    total += producto.precio
        return render_template('cart.html', cart_products=cart_products, total=total)
    else:
        return render_template('cart.html', message="Loguéate para agregar productos al carrito")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/api/products', methods=['GET'])
def api_get_products():
    productos = Producto.query.all()
    return jsonify([{'id': p.id, 'nombre': p.nombre, 'categoria': p.categoria, 'precio': p.precio, 'imagen': p.imagen} for p in productos])

@app.route('/api/products/<int:product_id>', methods=['GET'])
def api_get_product(product_id):
    producto = Producto.query.get(product_id)
    if producto:
        return jsonify({'id': producto.id, 'nombre': producto.nombre, 'categoria': producto.categoria, 'precio': producto.precio, 'imagen': producto.imagen})
    return jsonify({'error': 'Producto no encontrado'}), 404

@app.route('/api/products', methods=['POST'])
def api_add_product():
    data = request.get_json()
    nombre = data.get('nombre')
    categoria = data.get('categoria')
    precio = data.get('precio')
    imagen = data.get('imagen')
    agregar_producto(nombre, categoria, precio, imagen)
    return jsonify({'message': 'Producto agregado exitosamente'}), 201

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def api_update_product(product_id):
    data = request.get_json()
    nuevo_nombre = data.get('nombre')
    nueva_categoria = data.get('categoria')
    nuevo_precio = data.get('precio')
    nueva_imagen = data.get('imagen')
    actualizar_producto(product_id, nuevo_nombre, nueva_categoria, nuevo_precio, nueva_imagen)
    return jsonify({'message': 'Producto actualizado exitosamente'})

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def api_delete_product(product_id):
    eliminar_producto(product_id)
    return jsonify({'message': 'Producto eliminado exitosamente'})

if __name__ == '__main__':
    # Agregar productos iniciales solo si no hay productos en la base de datos
    with app.app_context():
        agregar_productos_iniciales()
        
        #Para eliminmar un prodcuto se puede hacer:
        
        #desde la consola ejecutar: curl -X DELETE http://localhost:5000/api/products/1

        #Para Agregar un producto se puede hacer:
        
        #desde la consola ejecutar curl -X POST http://localhost:5000/api/products \
        #-H "Content-Type: application/json" \
        #-d '{"nombre": "Cafetera", "categoria": "Categoria 3", "precio": 220000, "imagen": "cafetera.jpg"}'

        #para actualizar un producto se puede hacer:
        
        #desde la consola curl -X PUT http://localhost:5000/api/products/12 \
        #-H "Content-Type: application/json" \
        #-d '{"nombre": "Cafetera Nueva", "categoria": "Categoria 3", "precio": 3, "imagen": "cafetera_nueva.jpg"}'


    
    
    
    
    app.run(debug=True)

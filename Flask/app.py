from flask import Flask, render_template, redirect, url_for, session, flash
import mariadb
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "utviklinghemmelighet")


def hent_produkt(produkt_id):
    try:
        with mariadb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host="localhost",
            port=3306,
            database=os.getenv("DB_NAME")) as conn:

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM produkter WHERE id = ?", (produkt_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "navn": row[1],
                "pris": row[2],
                "beskrivelse": row[3],
                "lager": row[4],
            }
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None


def hent_produkter():
    try:
        with mariadb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host="localhost",
            port=3306,
            database=os.getenv("DB_NAME")) as conn:

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM produkter")
            return cursor.fetchall()
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return []


@app.route('/')
def hjem():
    produkter = hent_produkter()
    return render_template(
        'index.html',
        produkter=produkter,
        cart=session.get('cart', []),
        history=session.get('history', []),
    )


@app.route('/legg_i_handlekurv/<int:produkt_id>')
def legg_i_handlekurv(produkt_id):
    produkt = hent_produkt(produkt_id)
    if not produkt:
        flash("Produktet finnes ikke.", "error")
        return redirect(url_for('hjem'))

    cart = session.get('cart', [])
    for item in cart:
        if item['id'] == produkt['id']:
            item['antall'] += 1
            break
    else:
        cart.append({
            'id': produkt['id'],
            'navn': produkt['navn'],
            'pris': produkt['pris'],
            'antall': 1,
        })

    session['cart'] = cart
    flash(f"{produkt['navn']} er lagt til i handlekurven.", "success")
    return redirect(url_for('hjem'))


@app.route('/sjekk_ut')
def sjekk_ut():
    cart = session.get('cart', [])
    if not cart:
        flash("Handlekurven er tom.", "error")
        return redirect(url_for('hjem'))

    history = session.get('history', [])
    history.extend(cart)
    session['history'] = history
    session['cart'] = []
    flash("Kjøpet er fullført. Varene ligger nå i historikken.", "success")
    return redirect(url_for('hjem'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

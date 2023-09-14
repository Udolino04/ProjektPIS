from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)

class Automobil(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    marka = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    registracija = db.Column(db.String(20), nullable=False)
    kilometri = db.Column(db.Integer, nullable=False)
    vlasnik = db.Column(db.String(100), nullable=False)
    godina_proizvodnje = db.Column(db.Integer, nullable=False)
    
    popravci_u_tijeku = db.relationship('PopravakUTijeku', backref='automobil', lazy=True)
    povijest_popravaka = db.relationship('PovijestPopravaka', backref='automobil', lazy=True)
        
class PopravakUTijeku(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    automobil_id = db.Column(db.Integer, db.ForeignKey('automobil.id'), nullable=False)
    opis = db.Column(db.String(500), nullable=False)
    datum = db.Column(db.String(50), nullable=False)

class PovijestPopravaka(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    automobil_id = db.Column(db.Integer, db.ForeignKey('automobil.id'), nullable=False)
    opis = db.Column(db.String(500), nullable=False)
    datum = db.Column(db.String(50), nullable=False)

@app.route('/')
def index():
    automobili = Automobil.query.all()
    popravci_u_tijeku = PopravakUTijeku.query.all()
    return render_template('index.html', automobili=automobili, popravci_u_tijeku=popravci_u_tijeku)

@app.route('/obrisi_sve', methods=['POST'])
def obrisi_sve():
    db.session.query(PopravakUTijeku).delete()
    db.session.query(PovijestPopravaka).delete()
    db.session.query(Automobil).delete()
    db.session.commit()
    return redirect('/')

@app.route('/dodaj_automobil', methods=['POST'])
def dodaj_automobil():
    marka = request.form.get('marka')
    model = request.form.get('model')
    registracija = request.form.get('registracija')
    kilometri = int(request.form.get('kilometri'))
    vlasnik = request.form.get('vlasnik')
    godina_proizvodnje = int(request.form.get('godina_proizvodnje'))

    novi_automobil = Automobil(marka=marka, model=model, registracija=registracija, kilometri=kilometri, vlasnik=vlasnik, godina_proizvodnje=godina_proizvodnje)
    db.session.add(novi_automobil)
    db.session.commit()
    return redirect('/')

@app.route('/dodaj_popravak', methods=['POST'])
def dodaj_popravak():
    registracija = request.form.get('registracija')
    opis = request.form.get('opis')
    datum = request.form.get('datum')
    
    automobil = Automobil.query.filter_by(registracija=registracija).first()

    if automobil:
        novi_popravak = PopravakUTijeku(automobil_id=automobil.id, opis=opis, datum=datum)
        db.session.add(novi_popravak)
        db.session.commit()
        return redirect('/')
    else:
        return "Automobil s registracijom {} nije pronađen.".format(registracija)

@app.route('/zavrsi_popravak/<int:popravak_id>', methods=['GET', 'POST'])
def zavrsi_popravak(popravak_id):
    popravak = PopravakUTijeku.query.get_or_404(popravak_id)
    automobil = popravak.automobil

    novi_povijest_popravka = PovijestPopravaka(automobil_id=automobil.id, opis=popravak.opis, datum=popravak.datum)
    db.session.add(novi_povijest_popravka)
    db.session.delete(popravak) 
    db.session.commit()

    return redirect('/')

@app.route('/izbrisi_popravak/<int:popravak_id>', methods=['POST'])
def izbrisi_popravak(popravak_id):
    popravak = PopravakUTijeku.query.get_or_404(popravak_id)
    
    db.session.delete(popravak)
    db.session.commit()
    return redirect('/')


@app.route('/uredi_popravak/<int:popravak_id>', methods=['GET', 'POST'])
def uredi_popravak(popravak_id):
    popravak = PopravakUTijeku.query.get(popravak_id)

    if request.method == 'POST':
        popravak.opis = request.form.get('opis')
        popravak.datum = request.form.get('datum')
        db.session.commit()
        return redirect('/')
    
    return render_template('uredi_popravak.html', popravak=popravak)



@app.route('/povijest_popravaka', methods=['GET'])
def prikazi_povijest_popravaka():
    povijest_popravaka = PovijestPopravaka.query.all()
    
    return render_template('povijest_popravaka.html', povijest_popravaka=povijest_popravaka)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)

app.jinja_env.cache = {}
app.jinja_env.globals['enumerate'] = enumerate

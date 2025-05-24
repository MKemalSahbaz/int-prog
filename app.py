# Hocam, gerekli Flask modüllerini import ettim
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Hocam, Flask uygulamasını oluşturdum ve güvenlik için secret key tanımladım
app = Flask(__name__)
app.secret_key = 'gizli_anahtar'  # Hocam, production'da değiştirilmesi gerektiğini biliyorum
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///personel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Kullanıcı Modeli
class Kullanici(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kullanici_adi = db.Column(db.String(50), unique=True, nullable=False)
    sifre_hash = db.Column(db.String(128), nullable=False)

# Personel Modeli
class Personel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(50), nullable=False)
    soyad = db.Column(db.String(50), nullable=False)
    pozisyon = db.Column(db.String(50), nullable=False)
    maas = db.Column(db.Float, nullable=False)
    baslangic_tarihi = db.Column(db.String(20), nullable=False)
    durum = db.Column(db.String(20), nullable=False)
    aciklama = db.Column(db.Text)
    girisler = db.relationship('GirisCikis', backref='personel', lazy=True, cascade='all, delete-orphan')

# Giriş-Çıkış Modeli
class GirisCikis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    personel_id = db.Column(db.Integer, db.ForeignKey('personel.id'), nullable=False)
    tarih = db.Column(db.String(20), nullable=False)
    giris_saati = db.Column(db.String(10), nullable=False)
    cikis_saati = db.Column(db.String(10))

# İlk çalıştırmada admin kullanıcısı ekle
@app.before_first_request
def create_tables():
    db.create_all()
    if not Kullanici.query.filter_by(kullanici_adi='admin').first():
        admin = Kullanici(kullanici_adi='admin', sifre_hash=generate_password_hash('admin123'))
        db.session.add(admin)
        db.session.commit()

# Hocam, ana sayfamız burası, sistemi tanıtan bir landing page
@app.route('/')
def tanitim():
    return render_template('tanitim.html')

# Hocam, yönetim panelimiz. Session kontrolü ile güvenliği sağladım
@app.route('/panel')
def index():
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
    personeller = Personel.query.all()
    return render_template('index.html', personeller=personeller)

# Hocam, login işlemlerini burada yapıyoruz
@app.route('/giris', methods=['GET', 'POST'])
def giris():
    if request.method == 'POST':
        kullanici_adi = request.form['kullanici_adi'].strip()
        sifre = request.form['sifre'].strip()
        kullanici = Kullanici.query.filter_by(kullanici_adi=kullanici_adi).first()
        if kullanici and check_password_hash(kullanici.sifre_hash, sifre):
            session['kullanici'] = kullanici_adi
            return redirect(url_for('index'))
        else:
            flash('Hatalı kullanıcı adı veya şifre!')
    return render_template('giris.html')

# Hocam, kullanıcı kayıt sistemi
@app.route('/kayit', methods=['GET', 'POST'])
def kayit():
    if request.method == 'POST':
        kullanici_adi = request.form['kullanici_adi'].strip()
        sifre = request.form['sifre'].strip()
        sifre_tekrar = request.form['sifre_tekrar'].strip()
        if sifre != sifre_tekrar:
            flash('Şifreler uyuşmuyor!')
            return render_template('kayit.html')
        if Kullanici.query.filter_by(kullanici_adi=kullanici_adi).first():
            flash('Bu kullanıcı adı zaten alınmış!')
            return render_template('kayit.html')
        yeni_kullanici = Kullanici(
            kullanici_adi=kullanici_adi,
            sifre_hash=generate_password_hash(sifre)
        )
        db.session.add(yeni_kullanici)
        db.session.commit()
        flash('Kayıt başarılı! Şimdi giriş yapabilirsiniz.')
        return redirect(url_for('giris'))
    return render_template('kayit.html')

# Hocam, personel ekleme fonksiyonumuz
@app.route('/personel-ekle', methods=['GET', 'POST'])
def personel_ekle():
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
    if request.method == 'POST':
        ad = request.form['ad'].strip()
        soyad = request.form['soyad'].strip()
        pozisyon = request.form['pozisyon'].strip()
        maas = float(request.form['maas'])
        baslangic_tarihi = request.form['baslangic_tarihi']
        durum = request.form['durum']
        aciklama = request.form.get('aciklama', '')
        yeni_personel = Personel(
            ad=ad,
            soyad=soyad,
            pozisyon=pozisyon,
            maas=maas,
            baslangic_tarihi=baslangic_tarihi,
            durum=durum,
            aciklama=aciklama
        )
        db.session.add(yeni_personel)
        db.session.commit()
        flash('Personel başarıyla eklendi!')
        return redirect(url_for('index'))
    return render_template('personel_ekle.html')

# Hocam, güvenli çıkış için session'ı temizliyoruz
@app.route('/cikis')
def cikis():
    session.pop('kullanici', None)
    return redirect(url_for('giris'))

# Hocam, personel detay sayfası
@app.route('/personel/<int:personel_id>')
def personel_detay(personel_id):
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
    personel = Personel.query.get_or_404(personel_id)
    return render_template('personel_detay.html', personel=personel)

# Hocam, personel düzenleme sayfası
@app.route('/personel-duzenle/<int:personel_id>', methods=['GET', 'POST'])
def personel_duzenle(personel_id):
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
    personel = Personel.query.get_or_404(personel_id)
    if request.method == 'POST':
        personel.ad = request.form['ad'].strip()
        personel.soyad = request.form['soyad'].strip()
        personel.pozisyon = request.form['pozisyon'].strip()
        personel.maas = float(request.form['maas'])
        personel.baslangic_tarihi = request.form['baslangic_tarihi']
        personel.durum = request.form['durum']
        personel.aciklama = request.form.get('aciklama', '')
        db.session.commit()
        flash('Personel bilgileri başarıyla güncellendi!')
        return redirect(url_for('personel_detay', personel_id=personel.id))
    return render_template('personel_duzenle.html', personel=personel)

# Hocam, raporlama sayfası
@app.route('/raporlar')
def raporlar():
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
    return render_template('raporlar.html')

# Hocam, ayarlar sayfası
@app.route('/ayarlar', methods=['GET', 'POST'])
def ayarlar():
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
    
    if request.method == 'POST':
        # Hocam, burada kullanıcı ayarları güncellenecek
        flash('Ayarlar başarıyla güncellendi!')
        return redirect(url_for('ayarlar'))
    
    return render_template('ayarlar.html')

@app.route('/personel-giris-cikis', methods=['GET', 'POST'])
def personel_giris_cikis():
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
    personeller = Personel.query.all()
    # Filtreler
    personel_id = request.args.get('personel_id', type=int)
    baslangic = request.args.get('baslangic')
    bitis = request.args.get('bitis')
    durum = request.args.get('durum')
    arama = request.args.get('arama', '').strip()

    kayitlar = GirisCikis.query
    if personel_id:
        kayitlar = kayitlar.filter_by(personel_id=personel_id)
    if baslangic:
        kayitlar = kayitlar.filter(GirisCikis.tarih >= baslangic)
    if bitis:
        kayitlar = kayitlar.filter(GirisCikis.tarih <= bitis)
    if arama:
        kayitlar = kayitlar.join(Personel).filter(
            (Personel.ad.ilike(f'%{arama}%')) | (Personel.soyad.ilike(f'%{arama}%'))
        )
    kayitlar = kayitlar.order_by(GirisCikis.tarih.desc()).all()
    return render_template('personel_giris_cikis.html', kayitlar=kayitlar, personeller=personeller, secili_personel=personel_id, secili_baslangic=baslangic, secili_bitis=bitis, secili_durum=durum, secili_arama=arama)

@app.route('/personel/<int:personel_id>/giris-cikis-ekle', methods=['POST'])
def giris_cikis_ekle(personel_id):
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
    tarih = request.form['tarih']
    giris_saati = request.form['giris_saati']
    cikis_saati = request.form.get('cikis_saati')
    yeni_kayit = GirisCikis(
        personel_id=personel_id,
        tarih=tarih,
        giris_saati=giris_saati,
        cikis_saati=cikis_saati
    )
    db.session.add(yeni_kayit)
    db.session.commit()
    flash('Giriş-çıkış kaydı başarıyla eklendi!')
    return redirect(url_for('personel_detay', personel_id=personel_id))

@app.route('/personel-giris-cikis/duzenle/<int:kayit_id>', methods=['POST'])
def giris_cikis_duzenle(kayit_id):
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
    
    tarih = request.form.get('tarih')
    giris_saati = request.form.get('giris_saati')
    cikis_saati = request.form.get('cikis_saati')
    
    # TODO: Veritabanında kayıt güncelleme işlemi yapılacak
    
    flash('Giriş-çıkış kaydı başarıyla güncellendi!')
    return redirect(url_for('personel_giris_cikis'))

@app.route('/giris-cikis-sil/<int:kayit_id>', methods=['POST'])
def giris_cikis_sil(kayit_id):
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
    kayit = GirisCikis.query.get_or_404(kayit_id)
    db.session.delete(kayit)
    db.session.commit()
    flash('Kayıt silindi!')
    return redirect(url_for('personel_giris_cikis'))

@app.route('/personel-sil/<int:personel_id>', methods=['POST'])
def personel_sil(personel_id):
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
    personel = Personel.query.get_or_404(personel_id)
    db.session.delete(personel)
    db.session.commit()
    flash('Personel silindi!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True) 
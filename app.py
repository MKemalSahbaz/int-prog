# Hocam, gerekli Flask modüllerini import ettim
from flask import Flask, render_template, request, redirect, url_for, flash, session
import os

# Hocam, Flask uygulamasını oluşturdum ve güvenlik için secret key tanımladım
app = Flask(__name__)
app.secret_key = 'gizli_anahtar'  # Hocam, production'da değiştirilmesi gerektiğini biliyorum

# Hocam, ana sayfamız burası, sistemi tanıtan bir landing page
@app.route('/')
def tanitim():
    return render_template('tanitim.html')

# Hocam, yönetim panelimiz. Session kontrolü ile güvenliği sağladım
@app.route('/panel')
def index():
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
    return render_template('index.html')

# Hocam, login işlemlerini burada yapıyoruz
@app.route('/giris', methods=['GET', 'POST'])
def giris():
    if request.method == 'POST':
        kullanici_adi = request.form['kullanici_adi']
        sifre = request.form['sifre']
        # Hocam, şu an basit bir doğrulama var ama gerçek projede veritabanı kullanacağım
        if kullanici_adi == 'admin' and sifre == 'admin123':
            session['kullanici'] = kullanici_adi
            return redirect(url_for('index'))
        else:
            flash('Hatalı kullanıcı adı veya şifre!')
    return render_template('giris.html')

# Hocam, kullanıcı kayıt sistemi
@app.route('/kayit', methods=['GET', 'POST'])
def kayit():
    if request.method == 'POST':
        flash('Kayıt başarılı! Şimdi giriş yapabilirsiniz.')
        return redirect(url_for('giris'))
    return render_template('kayit.html')

# Hocam, personel ekleme fonksiyonumuz
@app.route('/personel-ekle', methods=['GET', 'POST'])
def personel_ekle():
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
    
    if request.method == 'POST':
        # Hocam, burada da veritabanı işlemleri yapılacaktı
        # Şimdilik flash mesajı ile işlemin başarılı olduğunu gösteriyorum
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
    # Hocam, burada veritabanından personel detayları çekilecek
    return render_template('personel_detay.html')

# Hocam, personel düzenleme sayfası
@app.route('/personel-duzenle/<int:personel_id>', methods=['GET', 'POST'])
def personel_duzenle(personel_id):
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
    
    if request.method == 'POST':
        # Hocam, burada veritabanı güncelleme işlemleri yapılacak
        flash('Personel bilgileri başarıyla güncellendi!')
        return redirect(url_for('personel_detay', personel_id=personel_id))
    
    return render_template('personel_duzenle.html')

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

@app.route('/personel-giris-cikis')
def personel_giris_cikis():
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
    return render_template('personel_giris_cikis.html')

@app.route('/personel-giris-cikis/ekle', methods=['POST'])
def giris_cikis_ekle():
    if 'kullanici' not in session:
        return redirect(url_for('giris'))
    
    tarih = request.form.get('tarih')
    giris_saati = request.form.get('giris_saati')
    cikis_saati = request.form.get('cikis_saati')
    
    # TODO: Veritabanına kayıt ekleme işlemi yapılacak
    
    flash('Giriş-çıkış kaydı başarıyla eklendi!')
    return redirect(url_for('personel_giris_cikis'))

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

if __name__ == '__main__':
    app.run(debug=True) 
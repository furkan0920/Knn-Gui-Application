# -*- coding: utf-8 -*-

import sys
import time

#PyQt5 için kullanılan paketler
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QMainWindow, QMessageBox, QTableWidgetItem               
from PyQt5.QtGui import QIcon, QColor 
from PyQt5 import QtCore 
from PyQt5.QtGui import QPainter, QBrush, QPen 
from PyQt5.QtCore import Qt 

#Qt Designer ile tasarlanan pancerelere ait paketler
from ana_pencere import *
from oznitelik_olceklendirme import *
from performans_rapor import *


#Makine öğrenmesinde kullanılan paketler
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import train_test_split 
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix,classification_report
import re
from sklearn.preprocessing import MinMaxScaler


#Arayüz tanımlanması ve ekrana yüklenmesi
app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
uiana_pencere = Ui_MainWindow()
uiana_pencere.setupUi(MainWindow)
MainWindow.show()

oznitelik_olceklendirme = QtWidgets.QMainWindow()
uioznitelik_olceklendirme = Ui_oznitelik_olceklendirme()
uioznitelik_olceklendirme.setupUi(oznitelik_olceklendirme)

performans_rapor = QtWidgets.QMainWindow()
uiperformans_rapor = Ui_performans_rapor()
uiperformans_rapor.setupUi(performans_rapor)

'''
dosya_ac(): Bu fonksiyon ile pandas kütüphanesi sayesinde excel dosyasından 
verinin okunarak df1 adlı bir dataframe içerisine eklenmesi gerçekleştirilmiştir.
Daha sonra ise dataframe içerisindeki veriler, Qt designer tasarımı esnasında 
ana pencereye eklenen ve adı tablo1 olan table widget öğesine aktarılmaktadır.
Ayrıca table widget öğesinin satır ve sütun sayılarının dataframe nesnesindeki
satır ve sütun sayıları ile uyumlu olması için bazı kodlar da ilave edilmiştir.


'''
def dosya_ac():
    fileName = QFileDialog.getOpenFileName()
    if fileName:
        print(fileName[0])
        print(fileName[1])
    # Excel sayfasının yüklenmemsi
    xl = pd.ExcelFile(fileName[0])
    # Data frame içine aktarım
    df1 = xl.parse(xl.sheet_names[0])
    global parametresayisi
    parametresayisi = df1.shape[1]-1
    print(xl.sheet_names[0])
    print(df1.shape)
    print(df1.columns)
    

    # Tahmin bölümüne ait Table widget tablo 2 olarak isimlendirilmiştir.
    uiana_pencere.tablo2.clear()
     
    for n in range(len(df1.columns)):
        uiana_pencere.tablo1.setHorizontalHeaderItem(n, QTableWidgetItem(df1.columns[n].upper()))
        
    for n in range(len(df1.columns)-1):
        uiana_pencere.tablo2.setVerticalHeaderItem(n, QTableWidgetItem(df1.columns[n].upper()))

    # tablo 1 ve tablo 2'nin satır ve sütun sayılarının dataframe'e göre ayarlanması
    uiana_pencere.tablo1.setRowCount(df1.shape[0])
    uiana_pencere.tablo1.setColumnCount(df1.shape[1])
    uiana_pencere.tablo2.setRowCount(df1.shape[1]-1)
   
    global sheet
    sheet = xl.parse(xl.sheet_names[0])
#    print(sheet.iat[1,1])
    
    data = [[sheet.iat[r,c] for c in range (df1.shape[1])] for r in range(df1.shape[0])]
       
    for row, columnvalues in enumerate(data):
#        print(row, columnvalues)
        for column, value in enumerate(columnvalues):
#            print(column, value)
            uiana_pencere.tablo1.setItem(row, column, QTableWidgetItem(str(value)))
    
    uiana_pencere.statusbar.showMessage(" Dosya: " + fileName[0] + "     Tablo: " + xl.sheet_names[0] + "     Veri Sutunu Sayısı: " + str(df1.shape[1]) + "     Veri Satırı Sayısı: " + str(df1.shape[0]) + "     Toplam Öğe Sayısı: " + str(df1.shape[0]*df1.shape[1]))

'''
dosya_kapat(): Bu fonksiyon ile öncelikle Eğitim Bölümündeki tablo1 ile 
Tahmin Bölümündeki tablo2 isimli table widget'lerin içerikleri temizleniyor.
Daha sonra ise Eğitim Bölümündeki vs_tablo1/vs_tablo2/vs_tablo3/vs_tablo4 isimli 
table widget'lerin içeriği temizleniyor ve 50 sütunlu tablo1'in sütun başlıkları 
"BOS" olarak adlandırılıyor.
'''
def dosya_kapat():
    uiana_pencere.tablo1.setRowCount(0)
    uiana_pencere.tablo1.setRowCount(16)
    uiana_pencere.tablo1.setColumnCount(50)
    
    uiana_pencere.tablo2.setRowCount(0)
    uiana_pencere.tablo2.setRowCount(7)
    uiana_pencere.tablo2.setColumnCount(1)
    
    uiana_pencere.textBrowser.clear()
    uiana_pencere.vs_tablo1.clear()
    uiana_pencere.vs_tablo2.clear()
    uiana_pencere.vs_tablo3.clear()
    uiana_pencere.vs_tablo4.clear()
    
    for n in range(50):
        uiana_pencere.tablo1.setHorizontalHeaderItem(n, QTableWidgetItem('BOS'))
        
#     # QTableWidget tablosunun sütun genişliklerinin ayarlanması
#    for n in range(50):
#        uiana_pencere.tablo1.setColumnWidth(n,70)


'''
veriseti_bol(): Bu fonksiyon ile öncelikle verisetinin bağımsız ve bağımlı 
değişkenleri iki veri kümesine ayrılıyor. Daha sonra bu veri kümeleri 
uiana_pencere.testsize adlı spinbox widget'inde girilen test size değerine göre 
girdi eğitim ve test seti ile çıktı eğitim ve test setleri olmak üzere dört sete 
ayrılıyor. Daha sonra ise bu veri setleri Eğitim Bölümü sekmesinde yer alan 
vs_tablo1/vs_tablo2/vs_tablo3vs_tablo4 isimli table widget'lere aktarılarak 
her bir tabloya ait veri sayıları label widget kullanılarak ilgili tablo başlığının
yanına yazdırılıyor.
'''    
def veriseti_bol():
    
    #Eğitim ve test veri kümelerine ayırma
    X = sheet.iloc[:, :-1].values
    y = sheet.iloc[:, -1].values
    
    global X_train, X_test, y_train, y_test
    
    ts = uiana_pencere.testsize.value()/100 #spinboxtan değer int olarak geliyor...
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = ts, random_state = 0)
    print(X_train, X_test, y_train, y_test)
    
#    TABLO_1:
    print(X_train.shape[0], X_train.shape[1])
    uiana_pencere.vs_tablo1.setRowCount(X_train.shape[0])
    uiana_pencere.vs_tablo1.setColumnCount(X_train.shape[1])
    
    for satir in range(X_train.shape[0]):
        for sutun in range(X_train.shape[1]):
            uiana_pencere.vs_tablo1.setItem(satir, sutun, QTableWidgetItem(str(X_train[satir,sutun])))
        
    uiana_pencere.label_11.setText(str(X_train.shape[0]) + "x" + str(X_train.shape[1]) + "/" + str(X_train.shape[0] + X_test.shape[0]) )
    
#    TABLO_2:    
    print(X_test.shape[0], X_test.shape[1])
    uiana_pencere.vs_tablo2.setRowCount(X_test.shape[0])
    uiana_pencere.vs_tablo2.setColumnCount(X_test.shape[1])
    
    for satir in range(X_test.shape[0]):
        for sutun in range(X_test.shape[1]):
            uiana_pencere.vs_tablo2.setItem(satir, sutun, QTableWidgetItem(str(X_test[satir,sutun])))
          
    uiana_pencere.label_12.setText(str(X_test.shape[0]) + "x" + str(X_test.shape[1]) + "/" + str(X_train.shape[0] + X_test.shape[0]) )
    
#    TABLO_3:
    print(y_train.shape[0])
    uiana_pencere.vs_tablo3.setRowCount(y_train.shape[0])
    uiana_pencere.vs_tablo3.setColumnCount(1)
    
    for satir in range(y_train.shape[0]):
        uiana_pencere.vs_tablo3.setItem(satir, 0, QTableWidgetItem(str(y_train[satir])))
          
    uiana_pencere.label_13.setText(str(y_train.shape[0]) + "x1/" + str(y_train.shape[0] + X_test.shape[0]) )

#    TABLO_4:
    print(y_test.shape[0])
    uiana_pencere.vs_tablo4.setRowCount(y_test.shape[0])
    uiana_pencere.vs_tablo4.setColumnCount(1)
    
    for satir in range(y_test.shape[0]):
        uiana_pencere.vs_tablo4.setItem(satir, 0, QTableWidgetItem(str(y_test[satir])))
       
    uiana_pencere.label_14.setText(str(y_test.shape[0]) + "x1/" + str(y_train.shape[0] + X_test.shape[0]) )

'''
oznitelik_olceklendir(): Bu fonksiyon ile öznitelik ölçeklendirme işlemi için gereken 
kütüphaneler import edildikten sonra veri setindeki tüm değerler 0 ile 1 arasında bir
değere dönüştürülerek ölçeklendiriliyor. Daha sonra bu değerler oznitelik_olceklendirme 
isimli ve "ÖZNİTELİK ÖLÇEKLENDİRME SONUÇLARI" başlıklı yeni bir pencere ile, oo_tablo1/
oo_tablo2/oo_tablo3/oo_tablo4 isimli dört table widget ile ekrana yazdırılıyor.
'''
def oznitelik_olceklendir():
    
    #Özellik ölçeklendirme İşlemi  
    from sklearn.preprocessing import MinMaxScaler
    global X_train, X_test, y_train, y_test, scaler
    
    scaler = MinMaxScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.fit_transform(X_test)
    y_train = scaler.fit_transform(y_train.reshape(-1,1))
    y_test = scaler.fit_transform(y_test.reshape(-1,1))
    
    print("*"*100)
    print("*"*100)
    oznitelik_olceklendirme.show()
    
    #    TABLO_1:
    uioznitelik_olceklendirme.oo_tablo1.setRowCount(X_train.shape[0])
    uioznitelik_olceklendirme.oo_tablo1.setColumnCount(X_train.shape[1])
    
    for satir in range(X_train.shape[0]):
        for sutun in range(X_train.shape[1]):
            uioznitelik_olceklendirme.oo_tablo1.setItem(satir, sutun, QTableWidgetItem(str(X_train[satir,sutun])))
 
#    TABLO_2:    
    print(X_test.shape[0], X_test.shape[1])
    uioznitelik_olceklendirme.oo_tablo2.setRowCount(X_test.shape[0])
    uioznitelik_olceklendirme.oo_tablo2.setColumnCount(X_test.shape[1])
    
    for satir in range(X_test.shape[0]):
        for sutun in range(X_test.shape[1]):
            uioznitelik_olceklendirme.oo_tablo2.setItem(satir, sutun, QTableWidgetItem(str(X_test[satir,sutun])))
              
#    TABLO_3:
    print(y_train.shape[0])
    uioznitelik_olceklendirme.oo_tablo3.setRowCount(y_train.shape[0])
    uioznitelik_olceklendirme.oo_tablo3.setColumnCount(1)
    
    for satir in range(y_train.shape[0]):
        uioznitelik_olceklendirme.oo_tablo3.setItem(satir, 0, QTableWidgetItem(str(y_train[satir,0])))
          
#    TABLO_4:
    print(y_test.shape[0])
    uioznitelik_olceklendirme.oo_tablo4.setRowCount(y_test.shape[0])
    uioznitelik_olceklendirme.oo_tablo4.setColumnCount(1)
    
    for satir in range(y_test.shape[0]):
        uioznitelik_olceklendirme.oo_tablo4.setItem(satir, 0, QTableWidgetItem(str(y_test[satir,0])))
      
'''
ag_egitim(): Bu fonksiyon ile eğitim setinin KNN algoritmasına uydurulması amacıyla
uiana_pencere'de yer alan combobox'ların değerleri alınarak sınıflandırıya parametre 
olarak atanıyor  ve bu değerlere bağlı olarak eğitim setinin girdi ve çıktı değerlerine 
göre sınıflandırma işlemi gerçekleştiriliyor yani ağ eğitiliyor. Daha sonra eğitilen
ağ ile test seti sonuçları tahmin ediliyor. Bunun sonucuna göre elde edilen hata matrisi 
ve sınıflandırma raporu textBrowser widget ile "uiperformans_rapor" adı ve "Rapor Ekranı" 
başlığıyla ekrana yazdırılıyor.
'''

def ag_egitim():
    
    # Eğitim setinin KNN'e göre uydurulması
    from sklearn.neighbors import KNeighborsClassifier
    nb = int(uiana_pencere.nb.currentText())
    mt = uiana_pencere.metric.currentText()
    pv = int(uiana_pencere.p.currentText())
    
    global siniflandirici
    global KNeighborsClassifiers
    siniflandirici = KNeighborsClassifier(n_neighbors = nb, metric = mt, p = pv)
    print("nb,mt,pv")
    print(nb,mt,pv)
    siniflandirici.fit(X_train, y_train)
    
    # Test seti sonuçlarının tahmin edilmesi
    y_pred = siniflandirici.predict(X_test)
    
    # Hata matrisi ve sınıflandırma raporu
    from sklearn.metrics import confusion_matrix,classification_report
    hm = confusion_matrix(y_test, y_pred)
    print(classification_report(y_test, y_pred))

    performans_rapor.show()
    uiperformans_rapor.textBrowser.setText("HATA MATRİSİ:")
    uiperformans_rapor.textBrowser.append("-"*100)
    uiperformans_rapor.textBrowser.append(str(hm))
    uiperformans_rapor.textBrowser.append("-"*100)
    uiperformans_rapor.textBrowser.append("SINIFLANDIRMA RAPORU:")
    uiperformans_rapor.textBrowser.append("-"*100)
    uiperformans_rapor.textBrowser.append(str(classification_report(y_test, y_pred)))


'''
tahmin(): Bu fonksiyon ile öncelikle sonuçların yazdırılacağı textBrowser widget temizleniyor.
Daha sonra uiana_pencere'nin tahmin bölümü sekmesinde yer alan tablo2 isimli table widget'a
girilen değerlere göre tahmin yapılıyor. Eğer ağın ürettiği sonuç 1 ise sonuç başarılı, 
0 ise başarısız olarak değerlendiriliyor ve textBrowser widget ile ekrana yazdırılıyor. 
Bu esnada bir progressBar widget ile işleme görsellik katılarak sonuç progressBar ile de 
gösteriliyor. Daha sonra alternatif K değerleri hesaplanarak bulunan yeni en uygun k değeri 
ile model tekrar eğitilerek hata matrisi yeniden hesaplanıyor.
'''
def tahmin():
    
    uiana_pencere.textBrowser.clear()
    
    #Yeni veri için tahmin sonuçları
    girdi = []
    for n in range(parametresayisi):
        girdi.append(int(uiana_pencere.tablo2.item(n,0).text()))
    girdiler = np.array(girdi)
    print(girdiler)
    
    uiana_pencere.label_2.setText("Sonuç hesaplanıyor...")
    for v in range (0,101):
        uiana_pencere.progressBar.setValue(v)
        time.sleep(1/40)
    
    uiana_pencere.label_2.setText("Sonuç hesaplandı...")
    
    timer0 = QtCore.QTimer()
    
    def bar():
        uiana_pencere.label_2.setText("")
        uiana_pencere.progressBar.setValue(0)
 
    timer0.singleShot(1500, bar) 
    
    print(parametresayisi)
    print(girdiler)

    girdiler = scaler.fit_transform(girdiler.reshape(1,-1))
    print(girdiler)
        
    global siniflandirici
    y_pred2 = siniflandirici.predict(np.reshape(girdiler, (1, -1)))
    print("y_pred2")
    print(y_pred2)
    
    if y_pred2 == 1:
        sonuc = "BAŞARILI..."
        yp = "1"
    if y_pred2 == 0:
        sonuc = "BAŞARISIZ..."
        yp = "0"
        
    uiana_pencere.textBrowser.setText("Ağın Ürettiği Sonuç = " + yp)
    uiana_pencere.textBrowser.append("-"*50)
    uiana_pencere.textBrowser.append("\nSONUÇ :    " + sonuc )
    
    #Alternatif k değerleri
    hatalarListesi = []
    for i in range(1,31):
        global KNeighborsClassifier
        siniflandirici = KNeighborsClassifier(n_neighbors=i)
        siniflandirici.fit(X_train, y_train)
        pred_i = siniflandirici.predict(X_test)
        hatalarListesi.append(np.mean(pred_i != y_test))
    
    print(hatalarListesi)
    
    #yeni en uygun k değeri ile (az gürültülü) model tekrar eğitiliyor
    from sklearn.neighbors import KNeighborsClassifier
    siniflandirici = KNeighborsClassifier(n_neighbors = 8, metric = 'minkowski', p = 2)
    siniflandirici.fit(X_train, y_train)
    y_pred = siniflandirici.predict(X_test)
    
    from sklearn.metrics import confusion_matrix,classification_report
    hm = confusion_matrix(y_test, y_pred)
    
    print(classification_report(y_test, y_pred))



timer2 = QtCore.QTimer()
fade = 1



'''
son(): Bu fonksiyon ile program sonlandırılıyor.
'''
def son():
    sys.exit(app.exec_())    


'''
cikis_pencere(): Bu fonksiyon fader ve son fonksiyonlarını çağırarak ana pencerenin
solarak kapanmasını ve programın sonlandırılmasını sağlıyor.
''' 
def cikis_pencere():
   sys.exit(app.exec_())  
 
    
    
###############################################################################
##     ANA PENCEREDE BASILAN TUŞLARA GÖRE İLGİLİ FONKSİYON BAŞLATILIYOR      ##
###############################################################################
uiana_pencere.menu_ac.triggered.connect(dosya_ac)
uiana_pencere.menu_kapat.triggered.connect(dosya_kapat)
uiana_pencere.menu_cikis.triggered.connect(cikis_pencere)
uiana_pencere.pb_olustur.clicked.connect(veriseti_bol)
uiana_pencere.pb_ozellik.clicked.connect(oznitelik_olceklendir)
uiana_pencere.pb_egit.clicked.connect(ag_egitim)
uiana_pencere.pb_sonuc.clicked.connect(tahmin)
uiana_pencere.pb_exit.clicked.connect(cikis_pencere)

sys.exit(app.exec_())
# reseptit

Sovelluksen käynnistäminen:

Kopioi ensin tämän GitHub-repositorion linkki ja kloonaa repositorio omalle koneellesi komennolla git clone (linkki). Siirry sen jälkeen projektikansioon komennolla cd reseptit. Luo seuraavaksi virtuaaliympäristö komennolla python3 -m venv venv ja aktivoi se komennolla source venv/bin/activate. Asenna tarvittavat kirjastot komennolla pip install flask. Luo tietokanta suorittamalla komento sqlite3 database.db < schema.sql. Käynnistä sovellus komennolla flask run. Kun sovellus on käynnistynyt, komentoriville tulostuu osoite (esimerkiksi http://127.0.0.1:5000). Avaa tämä osoite selaimessa, jolloin sovellus on valmis käytettäväksi.

Sovelluksessa toimivat tällä hetkellä (2.8.) seuraavat ominaisuudet: 
- Käyttäjä voi luoda tunnuksen sekä kirjautua sisään ja ulos.
- Käyttäjä voi lisätä uusia reseptejä sekä muokata ja poistaa omia reseptejään.
- Käyttäjä voi tarkastella kaikkia sovellukseen lisättyjä reseptejä.
- Käyttäjä voi etsiä reseptejä hakusanan avulla.


Tavoitteet: 
- Sovelluksessa käyttäjät pystyvät jakamaan ruokareseptejään. Reseptissä lukee tarvittavat ainekset ja valmistusohje.
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään reseptejä ja muokkaamaan ja poistamaan niitä.
- Käyttäjä näkee sovellukseen lisätyt reseptit.
- Käyttäjä pystyy etsimään reseptejä hakusanalla.
- Käyttäjäsivu näyttää, montako reseptiä käyttäjä on lisännyt ja listan käyttäjän lisäämistä resepteistä.
- Käyttäjä pystyy valitsemaan esimerkiksi seuraavia luokitteluja:
    * Ruoan tyyppi: alkuruoka, pääruoka tai jälkiruoka
    * Ruokavalio: laktoositon, gluteeniton tai vegaaninen
- Käyttäjä pystyy antamaan reseptille kommentin ja arvosanan. Reseptistä näytetään kommentit ja keskimääräinen arvosana.

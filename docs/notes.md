# Proje Notlari

## Ana Akis

1. `producer/kafka_producer.py` sentetik kullanici oturumlari uretir.
2. Kafka `user-events` topic'i olaylari tasir.
3. `consumer/session_feature_consumer.py` olaylari oturum seviyesinde toplar.
4. Oturum ozellikleri ve tahminler PostgreSQL'e yazilir.
5. `app/main.py` FastAPI uclari uzerinden verileri sunar.
6. `frontend/` dashboard ekrani API'den aldigi verileri gorsellestirir.

## Teslimde Dikkat Edilecekler

- `.env` dosyasi paylasilmaz; `.env.example` uzerinden anlatilir.
- Buyuk CSV dosyalari ve model ciktilari repoya eklenmez.
- PostgreSQL tablolari `db/init.sql` ile kurulabilir olmalidir.
- Demo sirasinda once Docker servisleri, sonra API, consumer, producer ve frontend acilir.

## Opsiyonel Genisletmeler

- Spark streaming ciktisi sunumda canli event dagilimi gostermek icin kullanilabilir.
- Olist veri seti lokal PostgreSQL'e import edilirse dashboard'un Olist bolumu dolu gorunur.
- `ml/train_model.py`, gercek tuketici oturumlarindan olusan `session_features` tablosuyla buyer modelini yeniden egitir.

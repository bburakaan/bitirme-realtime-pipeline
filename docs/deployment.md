# Online Deployment

Bu proje online ortamda iki farkli sekilde calistirilabilir.

## 1. Render ile online demo

Render senaryosu frontend, FastAPI backend ve PostgreSQL'i online acar. Kafka/Spark gibi agir servisler yerine `ENABLE_DEMO_PRODUCER=true` ayariyla backend icinde kontrollu demo veri uretimi baslar. Bu sayede dashboard bos kalmaz ve public URL uzerinden calisir.

Adimlar:

1. GitHub reposunu Render'a bagla.
2. Root dizindeki `render.yaml` dosyasini Blueprint olarak sec.
3. Render `bitirme-api`, `bitirme-frontend` ve `bitirme-postgres` kaynaklarini olusturur.
4. Deploy bitince frontend URL'i ac:

```text
https://bitirme-frontend.onrender.com
```

Backend URL:

```text
https://bitirme-backend-qujr.onrender.com
```

Saglik kontrolu:

```text
https://bitirme-backend-qujr.onrender.com/health
```

Not: Render demo modu Kafka kullanmadan veri uretir. Bu, online sunumun sorunsuz acilmasi icindir.

## 2. VPS veya sunucu ile tam Kafka pipeline

Kafka, Zookeeper, PostgreSQL ve Spark servislerini tam haliyle calistirmak icin bir VPS uzerinde Docker Compose kullanmak daha uygundur.

```powershell
docker compose up -d
python -m db.init_db
python -m ml.train_intent_model
uvicorn app.main:app --host 0.0.0.0 --port 8000
python -m consumer.session_feature_consumer
python -m producer.kafka_producer
```

Bu senaryoda `ENABLE_DEMO_PRODUCER=false` kalmalidir. Canli veri Kafka producer ve consumer uzerinden akar.

## Hangi senaryo secilmeli?

- Public link ile hizli demo gerekiyorsa Render Blueprint yeterlidir.
- Hoca ozellikle Kafka'nin online ortamda gercekten calistigini gormek isterse VPS/Docker Compose senaryosu tercih edilmelidir.

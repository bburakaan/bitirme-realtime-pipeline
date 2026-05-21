# Realtime E-Commerce Pipeline

Kafka, PostgreSQL, FastAPI, React ve makine öğrenmesi bileşenleriyle hazırlanmış gerçek zamanlı e-ticaret izleme projesi.

Proje iki akışı bir arada gösterir:

- Sentetik kullanıcı oturumları Kafka'ya üretilir, tüketici servis tarafından oturum özelliklerine çevrilir ve satın alma tahmini yapılır.
- Online Shoppers Purchasing Intention veri setiyle eğitilen intent modeli FastAPI üzerinden örnek tahmin üretir.

## Mimari

```text
Producer -> Kafka -> Feature Consumer -> PostgreSQL -> FastAPI -> React Dashboard
                                |
                                +-> ML model inference / CSV metrics
```

Opsiyonel Spark dosyaları `spark/` altında tutulur. Ana çalışan pipeline Python consumer üzerinden ilerler; Spark tarafı proje sunumu veya ek deneyler için ayrı çalıştırılabilir.

## Klasörler

| Yol | Amaç |
| --- | --- |
| `producer/` | Kafka'ya sentetik e-ticaret olayları gönderir. |
| `consumer/` | Kafka olaylarını tüketir, oturum özellikleri çıkarır, PostgreSQL'e yazar. |
| `app/` | FastAPI backend servisidir. |
| `frontend/` | React + Vite dashboard uygulamasıdır. |
| `ml/` | Model eğitim ve veri hazırlama scriptleri. |
| `db/` | PostgreSQL tablo şeması. |
| `spark/` | Opsiyonel Spark streaming ve batch inference örnekleri. |
| `data/intent/` | Intent modeli için küçük eğitim veri seti. |

## Gereksinimler

- Python 3.11+
- Node.js 20+
- Docker Desktop
- Git

## Kurulum

1. Ortam değişkenlerini hazırla:

```powershell
Copy-Item .env.example .env
```

2. Python bağımlılıklarını kur:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Frontend bağımlılıklarını kur:

```powershell
cd frontend
npm install
cd ..
```

4. Servisleri başlat:

```powershell
docker compose up -d
```

PostgreSQL ilk açılışta `db/init.sql` dosyasındaki tabloları otomatik oluşturur. Var olan volume'u sıfırlamak gerekirse:

```powershell
docker compose down -v
docker compose up -d
```

## Çalıştırma

Intent modelini eğit:

```powershell
python -m ml.train_intent_model
```

FastAPI backend'i başlat:

```powershell
uvicorn app.main:app --reload
```

Kafka oturum tüketicisini ayrı terminalde başlat:

```powershell
python -m consumer.session_feature_consumer
```

Kafka producer'ı ayrı terminalde başlat:

```powershell
python -m producer.kafka_producer
```

React dashboard'u başlat:

```powershell
cd frontend
npm run dev
```

Varsayılan adresler:

- API: `http://127.0.0.1:8000`
- API sağlık kontrolü: `http://127.0.0.1:8000/health`
- Frontend: `http://localhost:5173`

## Kullanışlı Komutlar

Bu komutlar ana bileşenleri kısa yoldan çalıştırır:

```powershell
python local_realtime_pipeline.py api
python local_realtime_pipeline.py producer
python local_realtime_pipeline.py consumer
python local_realtime_pipeline.py demo-worker
python local_realtime_pipeline.py init-db
python local_realtime_pipeline.py train-intent
```

## Veri ve Model Notları

- `.env`, `.venv`, `frontend/node_modules`, loglar, metrik çıktıları ve büyük veri dosyaları Git'e eklenmez.
- `data/intent/online_shoppers_intention.csv` küçük olduğu için intent modeli eğitimi amacıyla repoda tutulur.
- `ml/saved_model/` ignore edilir. Model dosyaları lokal olarak `python -m ml.train_intent_model` veya `python -m ml.train_model` ile yeniden üretilebilir.
- Olist CSV dosyaları büyük olduğu için repoya eklenmez. Lokal analiz için `data/olist/` altında tutulabilir.

## API Uçları

- `GET /health`
- `GET /stats/summary`
- `GET /events/recent`
- `GET /sessions/recent`
- `GET /predictions/recent`
- `GET /olist/summary`
- `GET /olist/orders/recent`
- `GET /olist/payments/summary`
- `GET /intent/model-info`
- `POST /intent/predict`

## Opsiyonel Spark

Spark streaming örneği için Kafka connector paketiyle çalıştır:

```powershell
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 spark/stream_processor.py
```

Batch model inference örneği:

```powershell
spark-submit spark/model_inference.py
```

## Online Deploy

Public link uzerinden acilacak demo icin `render.yaml` dosyasi hazirdir. Render Blueprint olarak kullanildiginda frontend, FastAPI backend ve PostgreSQL birlikte olusturulur.

```text
https://bitirme-frontend.onrender.com
https://bitirme-backend-qujr.onrender.com/health
```

Render senaryosunda Kafka/Spark yerine `ENABLE_DEMO_PRODUCER=true` ile backend icinde demo veri uretimi calisir. Tam Kafka pipeline'i online gostermek gerekirse VPS/Docker Compose senaryosu kullanilmalidir.

Daha detayli notlar icin: `docs/deployment.md`

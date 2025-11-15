# OCR Paddle — запуск и использование

## 1. Скачивание контейнера

Чтобы загрузить контейнер с Docker Hub:

```bash
docker pull nottwist/ocr-paddle:latest
```

## 2. Запуск контейнера

Запуск сервиса OCR с поддержкой GPU и пробросом порта:

```bash
docker run --gpus all \
  --name ocr_paddle \
  -p 5000:5000 \
  -e PYTHONUNBUFFERED=1 \
  -e FLASK_ENV=production \
  -it nottwist/ocr-paddle:latest
```

## 3. Получение транскрипции изображения

Отправьте POST-запрос на /ocr, передав URL изображения:

```bash
curl -X POST \
  http://localhost:5000/ocr \
  -H "Content-Type: application/json" \
  -d '{
    "image": "https://i.oneme.ru/i?r=BTE2sh_eZW7g8kugOdIm2NotpNaJIDqdOujSA74ESuZwmuY5pM152IrTQmGGcdCTzW4"
  }'
```

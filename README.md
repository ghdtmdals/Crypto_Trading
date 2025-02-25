# 암호화폐 자동매매 프로그램 개발

---

---

## 개요

1. **프로젝트 개요**
    - **Upbit API를 활용한 암호화폐 자동매매 프로그램 개발**
    - **Data Source:**
        - **Upbit 암호화폐 가격 및 관련 데이터**
        - **암호화폐 관련 뉴스**
        - **Upbit 암호화폐 캔들 데이터**
    - **프로젝트의 핵심 목표는 다양한 종류의 데이터를 효율적으로 수집, 적재, 제공할 수 있는 환경을 
    구축하는 것**
    - **단순한 구조에서 시작해 점진적으로 구조를 고도화 하며 다양한 툴의 사용법을 습득하고자 함**
2. **핵심 기능**

    | **📃분류** | **💻기능** | **📒비고** |
    | --- | --- | --- |
    | **Upbit API** | **암호화폐 가격 수집 및 저장** | **MySQL Upbit 테이블 저장** |
    |  | **자산 현황 조회 및 매매 수행** |  |
    |  | **암호화폐 캔들 데이터 수집** | **90일 가격 캔들 데이터** |
    |  | **캔들 데이터 차트 이미지 변환 및 저장** | **Default: High Price 이용** |
    | **뉴스** | **암호화폐 관련 뉴스 제목 수집** | **뉴스 소스 추가 가능; 본문 수집 추가 예정** |
    |  | **감성분석 수행** | **Huggingface Pretrained Model 이용** |
    |  | **뉴스 제목 및 감성분석 결과 저장** | **MySQL News 테이블 저장** |
    | **딥러닝 모델** | **정형 및 비정형 데이터 통합 텐서 구성** |  |
    |  | **분류 기반 자동매매 의사결정** | **0: Negative, 1: Neutral, 2: Positive** |
    |  | **결과 기반 모델 파라미터 업데이트** |  |
    | **Airflow** | **데이터 수집 ~ 모델 평가 파이프라인 구성** | **1분 단위 Dag 구현** |
    |  | **API 호출 기반 태스크 수행** | **Flask 기반 API 구현** |
3. **Future Plan**
    - **뉴스 본문 수집 및 데이터 마트 구축**

---

---

## 프로젝트 구조

## 암호화폐 자동매매

```
📦Crypto_Trading
┣ 📂Data
┃ ┣ 📂News
┃ ┃ ┣ 📜__init__.py
┃ ┃ ┣ 📜coinpedia.py
┃ ┃ ┣ 📜coinpress.py
┃ ┃ ┣ 📜news_crawling.py
┃ ┃ ┗ 📜sentiment_analysis.py
┃ ┗ 📂Upbit
┃ ┃ ┣ 📜__init__.py
┃ ┃ ┣ 📜upbit_candle_data.py
┃ ┃ ┗ 📜upbit_data.py
┣ 📂Database
┃ ┣ 📜__init__.py
┃ ┣ 📜create_functions.sql
┃ ┣ 📜create_schedulers.sql
┃ ┣ 📜create_tables.sql
┃ ┗ 📜database.py
┣ 📂Model
┃ ┗ 📂Network
┃ ┃ ┣ 📜__init__.py
┃ ┃ ┣ 📜trade_nets.py
┃ ┃ ┗ 📜trade_strategy.py
┣ 📂Trade
┃ ┣ 📜__init__.py
┃ ┗ 📜trade.py
┣ 📂airflow
┃ ┣ 📂dags
┃ ┃ ┣ 📜dag.py
┃ ┃ ┗ 📜test_dag.py
┃ ┗ 📜airflow_test.py
┣ 📜Dockerfile
┣ 📜dag_api.py
┣ 📜docker-compose.yml
┣ 📜install_lib.sh
┣ 📜main.py
┣ 📜run_before_docker_compose.sh
┣ 📜set_env.sh
```

## Power BI 시각화

```
📦power_bi
┣ 📂metrics_calculation
┃ ┣ 📂__pycache__
┃ ┃ ┗ 📜custom_metrics.cpython-312.pyc
┃ ┣ 📜custom_metrics.py
┃ ┣ 📜metrics_calculation.py
┃ ┗ 📜test.ipynb
┣ 📂remote_dump
┃ ┣ 📜crypto_db.sql
┃ ┣ 📜remote_dump.sh
┃ ┗ 📜scheduler.log
┣ 📜.env
┣ 📜.gitignore
┣ 📜Dockerfile
┣ 📜cron.log
┣ 📜crontab_test.sh
┣ 📜docker-compose.yml
┣ 📜scheduled_task.sh
┗ 📜visualization.pbix
```

---

---

# 실행 예시

## Prerequisite

- **환경변수에 SHM_SIZE 할당**

```bash
source run_before_docker_compose.sh
```

- **Container 실행**

```bash
docker-compose up -d
```

## 기본 실행 예시 (무한 반복문 기반)

```bash
python main.py
```

## Airflow 기반

- **Flask API 실행**

```bash
python dag_api.py
```

- **localhost:8080 접속**

![Image](https://github.com/user-attachments/assets/4c20387b-0e2b-4c7c-85f6-ea0034637500)

- **crypto_trading Dag 활성화**

![Image](https://github.com/user-attachments/assets/52b6a19a-0bbb-43e0-88be-62b595d3d7f2)

![Image](https://github.com/user-attachments/assets/dc5abff5-5c4b-4604-bb8e-1385569d84f6)

## 단일 Local API 호출

- **Flask API 실행**

```bash
python dag_api.py
```

- **curl**

```bash
### Local
curl -X GET http://localhost:4000/test
```

```bash
### Inside A Container
curl -X GET http://trader:4000/test
```

- **requests**

```python
import requests
```

```python
### Local
resp = requests.get("http://localhost:4000/test")
resp.json()
```

```python
### Inside A Container
resp = requests.get("http://trader:4000/test")
resp.json()
```

- **의존적인 태스크로 구성되어 있기 때문에 API 실행 시 오류가 발생할 수 있음**
- **localhost:8080 → crypto_trading → graph 참고**
- **URI List**

```bash
/test: 작동 테스트, 암호화폐 명 출력 (dag_api.py의 app.coin_name)

/save-news: 뉴스 제목 수집 및 감성분석 수행 후 News 테이블에 저장

/save-price: 암호화폐 가격 수집 후 Upbit 테이블에 저장

/save-chart: 암호화폐 90일 캔들 데이터 수집 후 이미지 변환 뒤 /Database/chart_images에 저장

/trade: 암호화폐 자동매매 1회 실행 및 결과 Trade_Log에 저장

/eval-model: 딥러닝 기반 자동매매 모델 성능 평가
```

---

---

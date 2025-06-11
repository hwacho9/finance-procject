# Macro Finance Dashboard 📊

> **실시간 금융 데이터 시각화 플랫폼**  
> React + FastAPI 기반의 포괄적인 거시경제 지표 대시보드

## 🌟 프로젝트 개요

Macro Finance Dashboard는 실시간 금융 시장 데이터와 거시경제 지표를 제공하는 웹 기반 플랫폼입니다. 투자자와 애널리스트들이 시장 동향을 한눈에 파악할 수 있도록 설계되었습니다.

### 주요 기능

- **📈 실시간 시장 지수**: 미국, 유럽, 아시아 주요 지수 모니터링
- **💹 거시경제 지표**: PMI, 인플레이션, 고용지표 등 종합 분석
- **⚡ 변동성 지수**: VIX, VXN 등 시장 심리 지표
- **🛢️ 원자재 가격**: WTI, 브렌트유, 금, 구리 등 상품 시세
- **💱 환율 정보**: 주요 통화 쌍 실시간 환율
- **🔔 AI 기반 분석**: 시장 트렌드 분석 및 인사이트 (예정)
- **💳 구독 서비스**: Stripe 기반 프리미엄 기능 (예정)

## 🏗️ 기술 스택

### Frontend (예정)

- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **React Query** for server state management
- **Recharts/D3.js** for data visualization

### Backend

- **FastAPI** - 고성능 Python 웹 프레임워크
- **SQLAlchemy** - ORM 및 데이터베이스 관리
- **PostgreSQL** - 메인 데이터베이스
- **Redis** - 캐싱 및 세션 관리
- **Pydantic** - 데이터 검증 및 직렬화

### 데이터 소스

- **Yahoo Finance** - 주식 및 지수 데이터
- **Alpha Vantage** - 프리미엄 시장 데이터 (예정)
- **FRED API** - 연방준비제도 경제 지표 데이터 ✅

### 개발 환경

- **Docker & Docker Compose** - 컨테이너화된 개발 환경
- **pytest** - 테스트 프레임워크
- **Black & isort** - 코드 포맷팅
- **TDD** - 테스트 주도 개발

## 🚀 빠른 시작

### 사전 요구사항

- **Docker** (v20.10+)
- **Docker Compose** (v2.0+)
- **Git**

### 설치 및 실행

1. **레포지토리 클론**

   ```bash
   git clone <repository-url>
   cd macro-finance
   ```

2. **환경 변수 설정**

   ```bash
   cp .env.example .env
   # .env 파일을 편집하여 필요한 설정값 입력
   ```

3. **Docker Compose로 실행**

   ```bash
   # 모든 서비스 빌드 및 시작
   docker-compose up --build

   # 백그라운드 실행
   docker-compose up -d
   ```

4. **서비스 확인**
   - **API 문서**: http://localhost:8000/docs
   - **API 상태**: http://localhost:8000/health
   - **데이터베이스**: localhost:5432
   - **Redis**: localhost:6379

### 개별 서비스 실행

```bash
# 백엔드만 실행
docker-compose up backend

# 데이터베이스만 실행
docker-compose up db

# 로그 확인
docker-compose logs -f backend
```

## 📖 API 문서

### 주요 엔드포인트

#### 시장 지수 데이터

```http
GET /api/v1/market/indices                    # 모든 지역 주요 지수
GET /api/v1/market/indices?region=US          # 미국 지수만
GET /api/v1/market/indices?region=EU          # 유럽 지수만
GET /api/v1/market/indices?region=ASIA        # 아시아 지수만
GET /api/v1/market/indices/{symbol}           # 특정 지수 상세 (예: SP500, KOSPI)
GET /api/v1/market/quote/{symbol}             # 특정 지수 현재가
GET /api/v1/market/overview                   # 시장 개요
GET /api/v1/market/test-indices               # 변동성 지수 테스트
```

#### 경제 지표 데이터 (FRED API)

```http
GET /api/v1/economic/indicators           # 모든 경제 지표
GET /api/v1/economic/indicators/{code}    # 특정 지표 상세
GET /api/v1/economic/bonds               # 채권 수익률 지표
GET /api/v1/economic/employment          # 고용 지표
GET /api/v1/economic/inflation           # 인플레이션 지표
GET /api/v1/economic/monetary            # 통화 정책 지표
GET /api/v1/economic/financial-stability # 금융 안정성 지표
```

#### 상태 확인

```http
GET /health
GET /api/v1/market/health
GET /api/v1/economic/health
```

#### 캐시 관리

```http
POST /api/v1/market/refresh?region=US
POST /api/v1/economic/refresh?category=bonds
```

### 응답 예시

```json
{
  "us_indices": {
    "sp500": {
      "symbol": "SP500",
      "name": "S&P 500",
      "current_value": 4500.0,
      "change": 25.5,
      "change_percent": 0.57,
      "timestamp": "2024-01-15T10:30:00Z",
      "market_status": "open"
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 📈 지원하는 주가지수 (Alpha Vantage & Yahoo Finance API)

### 🇺🇸 미국 주요 지수 (`?region=US`)

| 지수 코드       | 지수 명                          | 데이터 소스 | 설명                   |
| --------------- | -------------------------------- | ----------- | ---------------------- |
| **DJIA**        | Dow Jones Industrial Average     | DIA (ETF)   | 다우존스 산업평균지수  |
| **SP500**       | S&P 500                          | SPY (ETF)   | S&P 500 지수           |
| **NASDAQ**      | NASDAQ Composite                 | QQQ (ETF)   | 나스닥 종합지수        |
| **RUSSELL2000** | Russell 2000                     | IWM (ETF)   | 러셀 2000 소형주 지수  |
| **PHLX_SOX**    | Philadelphia Semiconductor Index | SOXX (ETF)  | 필라델피아 반도체 지수 |

### 🇪🇺 유럽 주요 지수 (`?region=EU`)

| 지수 코드        | 지수 명       | 데이터 소스 | 설명           |
| ---------------- | ------------- | ----------- | -------------- |
| **EURO_STOXX50** | Euro Stoxx 50 | ^STOXX50E   | 유로 스톡스 50 |
| **FTSE100**      | FTSE 100      | ^FTSE       | 영국 FTSE 100  |
| **DAX**          | DAX           | ^GDAXI      | 독일 DAX 지수  |
| **CAC40**        | CAC 40        | ^FCHI       | 프랑스 CAC 40  |
| **IBEX35**       | IBEX 35       | ^IBEX       | 스페인 IBEX 35 |

### 🌏 아시아-태평양 주요 지수 (`?region=ASIA`)

| 지수 코드              | 지수 명            | 데이터 소스 | 설명                 |
| ---------------------- | ------------------ | ----------- | -------------------- |
| **NIKKEI225**          | Nikkei 225         | ^N225       | 일본 닛케이 225      |
| **TOPIX**              | TOPIX              | ^TPX        | 일본 TOPIX           |
| **SHANGHAI_COMPOSITE** | Shanghai Composite | 000001.SS   | 중국 상하이 종합지수 |
| **HANG_SENG**          | Hang Seng          | ^HSI        | 홍콩 항셍지수        |
| **KOSPI**              | KOSPI              | ^KS11       | 한국 코스피          |
| **KOSDAQ**             | KOSDAQ             | ^KQ11       | 한국 코스닥          |
| **ASX200**             | S&P/ASX 200        | ^AXJO       | 호주 ASX 200         |

### 📊 변동성 지수

| 지수 코드  | 지수 명             | 데이터 소스 | 설명               |
| ---------- | ------------------- | ----------- | ------------------ |
| **VIX**    | CBOE VIX            | ^VIX        | 미국 변동성 지수   |
| **VXN**    | NASDAQ Volatility   | ^VXN        | 나스닥 변동성 지수 |
| **VSTOXX** | European Volatility | ^V2X        | 유럽 변동성 지수   |
| **VKOSPI** | Korean Volatility   | ^VKOSPI     | 한국 변동성 지수   |

### 🛢️ 원자재 및 상품

| 상품 코드       | 상품 명           | 데이터 소스 | 설명             |
| --------------- | ----------------- | ----------- | ---------------- |
| **WTI_CRUDE**   | WTI Crude Oil     | CL=F        | WTI 원유 선물    |
| **BRENT_CRUDE** | Brent Crude Oil   | BZ=F        | 브렌트 원유 선물 |
| **NATURAL_GAS** | Natural Gas       | NG=F        | 천연가스 선물    |
| **GOLD**        | Gold Spot Price   | GC=F        | 금 현물 가격     |
| **SILVER**      | Silver Spot Price | SI=F        | 은 현물 가격     |
| **COPPER**      | Copper Futures    | HG=F        | 구리 선물        |

### 💱 환율 및 통화

| 통화 코드   | 통화 쌍         | 데이터 소스 | 설명             |
| ----------- | --------------- | ----------- | ---------------- |
| **EUR_USD** | EUR/USD         | EURUSD=X    | 유로/달러 환율   |
| **USD_JPY** | USD/JPY         | JPY=X       | 달러/엔 환율     |
| **GBP_USD** | GBP/USD         | GBPUSD=X    | 파운드/달러 환율 |
| **DXY**     | US Dollar Index | DX-Y.NYB    | 달러 인덱스      |

## 📊 지원하는 경제 지표 (FRED API)

### 🏦 채권 수익률 (`/api/v1/economic/bonds`)

| 지표 코드        | 지표 명                             | 설명                             |
| ---------------- | ----------------------------------- | -------------------------------- |
| **DGS2**         | 2-Year Treasury Rate                | 2년 만기 미국 국채 수익률        |
| **DGS10**        | 10-Year Treasury Rate               | 10년 만기 미국 국채 수익률       |
| **ICSBULL**      | ICE BofA US Corporate Bond Index    | ICE BofA 미국 회사채 지수        |
| **BAMLH0A0HYM2** | ICE BofA High Yield Master II Index | ICE BofA 하이일드 마스터 II 지수 |

### 👔 고용 지표 (`/api/v1/economic/employment`)

| 지표 코드  | 지표 명                 | 설명                         |
| ---------- | ----------------------- | ---------------------------- |
| **UNRATE** | Unemployment Rate       | 실업률 (%)                   |
| **PAYEMS** | Total Nonfarm Payrolls  | 비농업 급료 고용자 수 (천명) |
| **AHEPA**  | Average Hourly Earnings | 평균 시급 (달러/시간)        |

### 📈 인플레이션 지표 (`/api/v1/economic/inflation`)

| 지표 코드     | 지표 명                          | 설명                        |
| ------------- | -------------------------------- | --------------------------- |
| **CPIAUCSL**  | Consumer Price Index             | 소비자물가지수 (CPI)        |
| **PPIACO**    | Producer Price Index             | 생산자물가지수 (PPI)        |
| **T10YIE**    | 10-Year Breakeven Inflation Rate | 10년 기대 인플레이션율      |
| **USACPIALL** | Core CPI                         | 코어 CPI (식품·에너지 제외) |

### 💰 통화 정책 지표 (`/api/v1/economic/monetary`)

| 지표 코드    | 지표 명            | 설명                      |
| ------------ | ------------------ | ------------------------- |
| **FEDFUNDS** | Federal Funds Rate | 연방기금금리 (%)          |
| **M2SL**     | M2 Money Stock     | M2 통화공급량 (십억 달러) |

### 🏛️ 금융 안정성 지표 (`/api/v1/economic/financial-stability`)

| 지표 코드   | 지표 명                              | 설명                               |
| ----------- | ------------------------------------ | ---------------------------------- |
| **TEDRATE** | TED Spread                           | TED 스프레드 (%)                   |
| **STLFSI**  | St. Louis Fed Financial Stress Index | 세인트루이스 연은 금융스트레스지수 |

### 📋 선행 지표 (`/api/v1/economic/indicators/category/leading_indicators`)

| 지표 코드    | 지표 명              | 설명                      |
| ------------ | -------------------- | ------------------------- |
| **CLICKSA2** | Conference Board LEI | 컨퍼런스보드 선행경제지수 |

### 💻 API 사용 예시

```bash
# 모든 경제 지표 조회
curl http://localhost:8000/api/v1/economic/indicators

# 특정 지표 상세 조회 (10년 국채 수익률)
curl http://localhost:8000/api/v1/economic/indicators/DGS10

# 카테고리별 조회 (고용 지표)
curl http://localhost:8000/api/v1/economic/employment

# 인플레이션 지표만 조회
curl http://localhost:8000/api/v1/economic/inflation
```

### 🔑 FRED API 키 설정

경제 지표 데이터를 사용하려면 FRED API 키가 필요합니다:

1. [FRED API 키 발급](https://fred.stlouisfed.org/docs/api/api_key.html)
2. `.env` 파일에 추가:
   ```env
   FRED_API_KEY=your_fred_api_key_here
   ```
3. Docker Compose 재시작:
   ```bash
   docker-compose restart backend
   ```

**Note**: API 키가 설정되지 않은 경우 실제와 유사한 Mock 데이터가 제공됩니다.

## 📅 자동 데이터 갱신 시스템

### 🤖 FRED 데이터 스케줄러

효율적인 데이터 관리를 위해 각 경제 지표의 FRED 발표 주기에 맞춰 자동으로 데이터를 갱신합니다:

#### ⏰ 갱신 주기별 분류

| 주기     | 지표                                                                  | 갱신 시간                | 설명                         |
| -------- | --------------------------------------------------------------------- | ------------------------ | ---------------------------- |
| **일일** | DGS2, DGS10, T10YIE, FEDFUNDS, TEDRATE, BAMLH0A0HYM2                  | 매일 오전 6시 KST        | 채권 수익률 및 금리 데이터   |
| **주간** | M2SL, STLFSI                                                          | 매주 목요일 오전 6시 KST | 통화공급량, 금융스트레스지수 |
| **월간** | UNRATE, PAYEMS, AHEPA, CPIAUCSL, PPIACO, USACPIALL, CLICKSA2, ICSBULL | 매일 오후 11시 체크      | 고용, 인플레이션, 선행지표   |

#### 🎯 스마트 업데이트 로직

- **발표일 기반 갱신**: 각 지표의 실제 발표일에 맞춰 업데이트
- **중복 요청 방지**: 마지막 업데이트 시간과 비교하여 불필요한 API 호출 차단
- **백그라운드 처리**: 사용자 요청에 영향을 주지 않는 비동기 처리

#### 📊 스케줄러 API 엔드포인트

```bash
# 스케줄러 상태 확인
GET /api/v1/scheduler/status

# 스케줄러 시작/중지
POST /api/v1/scheduler/start
POST /api/v1/scheduler/stop

# 수동 업데이트 트리거
POST /api/v1/scheduler/update/manual              # 모든 지표
POST /api/v1/scheduler/update/indicator/{code}    # 특정 지표

# 스케줄 설정 조회
GET /api/v1/scheduler/schedules

# 스케줄러 헬스 체크
GET /api/v1/scheduler/health
```

#### 💾 데이터베이스 저장

스케줄러는 업데이트된 데이터를 다음 테이블에 저장합니다:

- `economic_indicators`: 실제 지표 데이터 (타임시리즈)
- `indicator_update_logs`: 업데이트 로그 및 성공/실패 기록
- `data_quality_checks`: 데이터 품질 검증 결과

#### 🔧 사용 예시

```bash
# 스케줄러 시작
curl -X POST http://localhost:8000/api/v1/scheduler/start

# 모든 지표 수동 업데이트
curl -X POST http://localhost:8000/api/v1/scheduler/update/manual

# 특정 지표 강제 업데이트 (예: 10년 국채 수익률)
curl -X POST http://localhost:8000/api/v1/scheduler/update/indicator/DGS10

# 스케줄러 상태 확인
curl http://localhost:8000/api/v1/scheduler/status
```

## 🧪 테스트

### 테스트 실행

```bash
# 백엔드 테스트
docker-compose exec backend pytest

# 커버리지 포함 테스트
docker-compose exec backend pytest --cov=app

# 특정 테스트 파일
docker-compose exec backend pytest app/tests/test_market_data_service.py -v
```

### 테스트 철학

프로젝트는 **TDD(테스트 주도 개발)** 방식을 따릅니다:

1. **Red**: 실패하는 테스트 작성
2. **Green**: 테스트를 통과하는 최소 코드 작성
3. **Refactor**: SOLID 원칙에 따른 리팩토링

## 🏛️ 아키텍처

### SOLID 원칙 적용

- **S (Single Responsibility)**: 각 클래스는 단일 책임
- **O (Open/Closed)**: 확장에는 열려있고 수정에는 닫혀있음
- **L (Liskov Substitution)**: 하위 타입은 상위 타입 대체 가능
- **I (Interface Segregation)**: 클라이언트별 최소 인터페이스
- **D (Dependency Inversion)**: 추상화에 의존, 구체 클래스에 의존하지 않음

### 폴더 구조

```
macro-finance/
├── backend/
│   ├── app/
│   │   ├── api/v1/           # API 라우터
│   │   │   └── providers/    # 외부 데이터 제공자
│   │   ├── core/             # 설정 및 데이터베이스
│   │   ├── schemas/          # Pydantic 스키마
│   │   ├── services/         # 비즈니스 로직
│   │   └── tests/            # 테스트 파일
│   │   └── main.py           # FastAPI 앱
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # React 앱 (예정)
├── database/                 # DB 초기화 스크립트
├── docker-compose.yml
└── README.md
```

## 🔧 개발 가이드

### 코드 스타일

```bash
# 코드 포맷팅
docker-compose exec backend black .
docker-compose exec backend isort .

# 린팅
docker-compose exec backend flake8
```

### 새로운 기능 추가

1. **테스트 작성** (TDD)

   ```python
   def test_should_do_something_when_condition():
       # Given
       # When
       # Then
   ```

2. **인터페이스 정의** (DIP)

   ```python
   class DataProvider(ABC):
       @abstractmethod
       async def get_data(self) -> Dict:
           pass
   ```

3. **구현 클래스 작성** (SRP)
   ```python
   class ConcreteProvider(DataProvider):
       async def get_data(self) -> Dict:
           # 구현
   ```

### 데이터베이스 마이그레이션

```bash
# 마이그레이션 생성
docker-compose exec backend alembic revision --autogenerate -m "description"

# 마이그레이션 실행
docker-compose exec backend alembic upgrade head
```

## 🌐 환경 변수

### 필수 환경 변수

```env
# 데이터베이스
DATABASE_URL=postgresql://postgres:postgres@db:5432/macro_finance
POSTGRES_DB=macro_finance
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Redis
REDIS_URL=redis://redis:6379

# API 설정
SECRET_KEY=your-secret-key-here
DEBUG=True
CORS_ORIGINS=http://localhost:3000
```

### 선택적 환경 변수

```env
# 외부 API 키 (프리미엄 데이터용)
ALPHA_VANTAGE_API_KEY=your-api-key
FRED_API_KEY=your-api-key

# Stripe (결제 서비스용)
STRIPE_SECRET_KEY=your-stripe-key
STRIPE_WEBHOOK_SECRET=your-webhook-secret
```

## 🚀 배포

### 개발 환경

```bash
docker-compose up
```

### 프로덕션 환경

```bash
docker-compose -f docker-compose.prod.yml up
```

## 🔮 향후 계획

### Phase 1 (현재)

- ✅ FastAPI 백엔드 구축
- ✅ 시장 지수 데이터 API
- ✅ Docker 개발 환경

### Phase 2 (진행 예정)

- 🔄 React 프론트엔드 개발
- 🔄 실시간 데이터 WebSocket
- 🔄 사용자 인증 시스템

### Phase 3 (계획)

- 📋 AI 기반 시장 분석
- 📋 Stripe 결제 시스템
- 📋 프리미엄 구독 기능
- 📋 알림 서비스

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 기여 가이드라인

- **TDD** 원칙 준수
- **SOLID** 원칙 적용
- **코드 커버리지 80%** 이상 유지
- **Conventional Commits** 사용

## 📝 라이선스

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 문의

- **이슈**: GitHub Issues
- **이메일**: your-email@example.com

---

**Made with ❤️ for the financial community**

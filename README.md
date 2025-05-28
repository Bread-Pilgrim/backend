## 목차

- [Project Architecture](#project-architecture)
  - [🗂️ 폴더 구조](#-폴더-구조)

--- 

# Project Architecture
> ### 유지보수성과 확장성을 고려해서, 각 계층을 분리하고 책임을 명확히 하도록 구성하려고 노력했습니다.

--- 

## 🗂️ 폴더 구조

```
app/
├── main.py
├── api/
│ ├── v1/
│ │ ├── endpoints/
│ └── router.py
├── core/
│ ├── config.py
│ ├── security.py
│ └── logging.py
├── models/
├── schemas/
├── services/
├── repositories/
├── db/
├── utils/
└── tests/                      
    ├── conftest.py           
    ├── api/
    ├── services/
    ├── repositories/
    └── schemas/
```
<details>
<summary><strong>main.py</strong></summary>

애플리케이션 진입점으로, 라우터 및 미들웨어 설정을 담당합니다.

</details>

<details>
<summary><strong>api/</strong></summary>

API 라우터들을 정의합니다. version별 디렉토리 구조로 구성되어 있고, endpoint들이 포함되어 있습니다.

- `v1/endpoints/`: 유저, 게시글 등 각 도메인별 API 엔드포인트 파일  
- `router.py`: 버전별 라우터를 하나로 묶어 FastAPI에 등록  

</details>

<details>
<summary><strong>core/</strong></summary>

애플리케이션의 핵심 설정을 담고 있습니다.

- `config.py`: 환경 설정 및 설정 객체 정의  
- `security.py`: 보안 관련 로직 ( 토큰 생성, 비밀번호 해시화 등 )
- `logging.py`: 로깅 설정  

</details>

<details>
<summary><strong>models/</strong></summary>

데이터베이스 모델을 SQLAlchemy로 정의하고 있습니다.

</details>

<details>
<summary><strong>schemas/</strong></summary>

요청/응답에 사용되는 Pydantic 기반 스키마 정의하고 있습니다.

</details>

<details>
<summary><strong>services/</strong></summary>

비즈니스 로직이 위치하는 계층입니다. 하나의 유스케이스 단위로 서비스를 구성합니다.

</details>

<details>
<summary><strong>repositories/</strong></summary>

데이터베이스 접근 로직을 담당하는 계층입니다. SQLAlchemy 세션이나 MySQLDB 클라이언트를 통해 데이터를 직접 조회/수정합니다.

</details>

<details>
<summary><strong>db/</strong></summary>

데이터베이스 초기화, 테이블 생성, 세션 관리 등을 담당합니다.

- `base.py`: Base 모델 등록  
- `session.py`: DB 세션 설정  
- `init_db.py`: 초기 데이터 삽입 및 마이그레이션 작업

</details>

<details>
<summary><strong>utils/</strong></summary>

공통적으로 사용되는 유틸리티 함수들을 정의합니다.

</details>

<details>
<summary><strong>tests/</strong></summary>

Pytest 기반 테스트 코드가 위치하는 디렉터리입니다.

- `conftest.py`: 공통 fixture 정의 (FastAPI 클라이언트, 테스트 DB 등)  
- `api/`: API 엔드포인트 테스트  
- `services/`: 서비스 계층 유닛 테스트  
- `repositories/`: 데이터 접근 계층 테스트  
- `schemas/`: Pydantic 스키마 유효성 테스트  

</details>

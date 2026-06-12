# 환자관리 API 명세서

## 공통 사항

| 항목 | 내용 |
| --- | --- |
| Base URL | `/api/v1` |
| 인증 방식 | JWT Bearer Token |
| Access Token 만료 | 30분 |
| Refresh Token 만료 | 7일 |
| 공통 응답 시간 | 최대 3초 이내 |
| 이미지 저장 위치 | 서버가 실행되는 환경의 로컬 저장소 |

### 공통 Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | `application/json` | JSON 요청 타입 |
| Content-Type | `multipart/form-data` | X-Ray 이미지 업로드 요청 타입 |
| Authorization | `Bearer <access_token>` | 인증이 필요한 API 호출 시 사용 |

### 공통 Enum

| 구분 | 값 | 설명 |
| --- | --- | --- |
| gender | `M`, `F` | 성별 |
| role | `STAFF`, `ADMIN` | 환자관리/진료기록 API 접근 가능 권한 |

---

## 1. 환자 정보 등록 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 환자 정보 등록 API |
| 설명 | 사내 의료인 역할을 가진 사용자가 환자 정보를 시스템에 등록하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/` |
| 메서드(Method) | `POST` |
| 인증 필요 여부 | Y, `STAFF` 또는 `ADMIN` 권한 필요 |

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | `application/json` | 요청 타입 |
| Authorization | `Bearer <access_token>` | JWT 액세스 토큰 |

#### 본문 예시

```json
{
  "name": "김환자",
  "age": 45,
  "gender": "M",
  "phone": "01012345678"
}
```

#### 본문 필드

| 파라미터명 | 타입 | 필수(Y/N) | 설명 |
| --- | --- | --- | --- |
| name | string | Y | 환자 이름 |
| age | integer | Y | 환자 나이 |
| gender | string | Y | 환자 성별. `M`, `F` 중 하나 |
| phone | string | Y | 환자 연락처. 휴대폰 번호 |

#### 쿼리 파라미터

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| 없음 | - | - | - |

### 3. 응답(Response)

#### 성공

`201 Created`

```json
{
  "id": 1,
  "name": "김환자",
  "age": 45,
  "gender": "M",
  "phone": "01012345678",
  "created_at": "2026-06-09T10:00:00",
  "updated_at": null
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 환자 고유 ID |
| name | string | 환자 이름 |
| age | integer | 환자 나이 |
| gender | string | 환자 성별 |
| phone | string | 환자 연락처 |
| created_at | datetime | 생성일시 |
| updated_at | datetime/null | 수정일시 |

#### 실패

`400 Bad Request`

```json
{
  "detail": "입력값이 올바르지 않습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `invalid_input`: 입력값 형식 오류, `empty_fields`: 필수 필드 누락 |

### 4. 비고

환자 정보 등록은 `STAFF` 또는 `ADMIN` 권한 사용자만 가능하다. `PENDING` 권한 사용자는 환자관리 기능에 접근할 수 없다.

---

## 2. 환자 목록 조회 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 환자 목록 조회 API |
| 설명 | 로그인 사용자가 환자 목록을 조회하고 이름, 성별, 나이 범위로 검색/필터링하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/` |
| 메서드(Method) | `GET` |
| 인증 필요 여부 | Y, `STAFF` 또는 `ADMIN` 권한 필요 |

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Authorization | `Bearer <access_token>` | JWT 액세스 토큰 |

#### 본문 예시

```json
{}
```

#### 본문 필드

| 파라미터명 | 타입 | 필수(Y/N) | 설명 |
| --- | --- | --- | --- |
| 없음 | - | - | - |

#### 쿼리 파라미터

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| search | string | N | 환자 이름 검색어 |
| gender | string | N | 성별 필터. `M`, `F` 중 하나 |
| min_age | integer | N | 최소 나이 |
| max_age | integer | N | 최대 나이 |
| page | integer | N | 페이지 번호. 기본값 `1` |
| size | integer | N | 페이지당 조회 수. 기본값 `20` |

### 3. 응답(Response)

#### 성공

`200 OK`

```json
{
  "total": 1,
  "page": 1,
  "size": 20,
  "items": [
    {
      "id": 1,
      "name": "김환자",
      "age": 45,
      "gender": "M",
      "phone": "01012345678",
      "created_at": "2026-06-09T10:00:00",
      "updated_at": null
    }
  ]
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| total | integer | 검색/필터 조건을 반영한 전체 환자 수 |
| page | integer | 현재 페이지 번호 |
| size | integer | 페이지당 조회 수 |
| items | array | 환자 목록 |

#### 실패

`400 Bad Request`

```json
{
  "detail": "나이 범위가 올바르지 않습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `invalid_gender`: 성별 값 오류, `invalid_age_range`: 나이 범위 오류, `invalid_page`: 페이지 값 오류 |

### 4. 비고

목록 조회 시 확인 가능한 항목은 환자 고유 ID, 이름, 나이, 성별, 연락처, 생성일시, 수정일시이다.

---

## 3. 환자 정보 상세 조회 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 환자 정보 상세 조회 API |
| 설명 | 로그인 사용자가 특정 환자의 상세 정보를 조회하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/{patient_id}/` |
| 메서드(Method) | `GET` |
| 인증 필요 여부 | Y, `STAFF` 또는 `ADMIN` 권한 필요 |

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Authorization | `Bearer <access_token>` | JWT 액세스 토큰 |

#### 본문 예시

```json
{}
```

#### 본문 필드

| 파라미터명 | 타입 | 필수(Y/N) | 설명 |
| --- | --- | --- | --- |
| 없음 | - | - | - |

#### 쿼리 파라미터

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| 없음 | - | - | - |

### 3. 응답(Response)

#### 성공

`200 OK`

```json
{
  "id": 1,
  "name": "김환자",
  "age": 45,
  "gender": "M",
  "phone": "01012345678",
  "created_at": "2026-06-09T10:00:00",
  "updated_at": null
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 환자 고유 ID |
| name | string | 환자 이름 |
| age | integer | 환자 나이 |
| gender | string | 환자 성별 |
| phone | string | 환자 연락처 |
| created_at | datetime | 생성일시 |
| updated_at | datetime/null | 수정일시 |

#### 실패

`404 Not Found`

```json
{
  "detail": "환자를 찾을 수 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `patient_not_found`: 대상 환자 없음 |

### 4. 비고

상세 조회 가능한 항목은 이름, 성별, 연락처, 나이이다. API 응답에는 화면 표시 및 추적을 위해 고유 ID, 생성일시, 수정일시도 포함한다.

---

## 4. 환자 정보 수정 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 환자 정보 수정 API |
| 설명 | 로그인 사용자가 특정 환자의 이름과 연락처를 부분 수정하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/{patient_id}/` |
| 메서드(Method) | `PATCH` |
| 인증 필요 여부 | Y, `STAFF` 또는 `ADMIN` 권한 필요 |

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | `application/json` | 요청 타입 |
| Authorization | `Bearer <access_token>` | JWT 액세스 토큰 |

#### 본문 예시

```json
{
  "name": "김수정",
  "phone": "01098765432"
}
```

#### 본문 필드

| 파라미터명 | 타입 | 필수(Y/N) | 설명 |
| --- | --- | --- | --- |
| name | string | N | 변경할 환자 이름 |
| phone | string | N | 변경할 환자 연락처 |

#### 쿼리 파라미터

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| 없음 | - | - | - |

### 3. 응답(Response)

#### 성공

`200 OK`

```json
{
  "id": 1,
  "name": "김수정",
  "age": 45,
  "gender": "M",
  "phone": "01098765432",
  "created_at": "2026-06-09T10:00:00",
  "updated_at": "2026-06-09T11:00:00"
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 환자 고유 ID |
| name | string | 변경된 환자 이름 |
| age | integer | 환자 나이 |
| gender | string | 환자 성별 |
| phone | string | 변경된 환자 연락처 |
| created_at | datetime | 생성일시 |
| updated_at | datetime/null | 수정일시 |

#### 실패

`400 Bad Request`

```json
{
  "detail": "수정 가능한 필드가 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `empty_update_fields`: 수정 필드 없음, `invalid_input`: 입력값 형식 오류 |

### 4. 비고

환자 정보 수정은 Partial Update로 처리한다. 요구사항 기준 수정 가능한 항목은 이름과 연락처로 제한한다.

---

## 5. 환자 정보 삭제 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 환자 정보 삭제 API |
| 설명 | 로그인 사용자가 특정 환자와 관련 진료기록, X-Ray 이미지를 영구 삭제하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/{patient_id}/` |
| 메서드(Method) | `DELETE` |
| 인증 필요 여부 | Y, `STAFF` 또는 `ADMIN` 권한 필요 |

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Authorization | `Bearer <access_token>` | JWT 액세스 토큰 |

#### 본문 예시

```json
{}
```

#### 본문 필드

| 파라미터명 | 타입 | 필수(Y/N) | 설명 |
| --- | --- | --- | --- |
| 없음 | - | - | - |

#### 쿼리 파라미터

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| 없음 | - | - | - |

### 3. 응답(Response)

#### 성공

`204 No Content`

```json
{}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| 없음 | - | 응답 본문 없음 |

#### 실패

`404 Not Found`

```json
{
  "detail": "환자를 찾을 수 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `patient_not_found`: 대상 환자 없음 |

### 4. 비고

삭제 전 클라이언트는 관련 데이터가 모두 삭제됨을 알리는 확인 팝업을 표시한다. 확인 후 서버는 해당 환자와 관련된 진료기록, X-Ray 이미지 데이터를 함께 영구 삭제한다.

---

## 6. 진료기록 등록 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 진료기록 등록 API |
| 설명 | 사내 의료인 역할을 가진 사용자가 환자의 진료정보와 흉부 X-Ray 이미지를 등록하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/{patient_id}/medical-records/` |
| 메서드(Method) | `POST` |
| 인증 필요 여부 | Y, `STAFF` 또는 `ADMIN` 권한 필요 |

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | `multipart/form-data` | 이미지 업로드 요청 타입 |
| Authorization | `Bearer <access_token>` | JWT 액세스 토큰 |

#### 본문 예시

```text
chart_number: "CHART-20260609-001"
symptoms: "기침과 흉통을 호소하며 흉부 X-Ray 촬영을 진행함"
shooting_datetime: "2026-06-09T09:30:00"
xray_image: chest-xray.png
```

#### 본문 필드

| 파라미터명 | 타입 | 필수(Y/N) | 설명 |
| --- | --- | --- | --- |
| chart_number | string | Y | 진료 차트 넘버. 중복 불가 |
| symptoms | string | Y | 진료된 증상 |
| shooting_datetime | datetime | Y | X-Ray 촬영 일시 |
| xray_image | file | Y | 촬영된 흉부 X-Ray 이미지 파일 |

#### 쿼리 파라미터

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| 없음 | - | - | - |

### 3. 응답(Response)

#### 성공

`201 Created`

```json
{
  "id": 1,
  "patient_id": 1,
  "chart_number": "CHART-20260609-001",
  "symptoms": "기침과 흉통을 호소하며 흉부 X-Ray 촬영을 진행함",
  "xray_image": {
    "id": 1,
    "image_url": "/media/xray/2026/06/chest-xray.png",
    "shooting_datetime": "2026-06-09T09:30:00"
  },
  "created_at": "2026-06-09T10:10:00",
  "updated_at": null
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 진료기록 ID |
| patient_id | integer | 환자 고유 ID |
| chart_number | string | 진료 차트 넘버 |
| symptoms | string | 진료된 증상 |
| xray_image | object | 업로드된 X-Ray 이미지 정보 |
| created_at | datetime | 생성일시 |
| updated_at | datetime/null | 수정일시 |

#### 실패

`400 Bad Request`

```json
{
  "detail": "이미 사용 중인 진료 차트 넘버입니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `duplicate_chart_number`: 차트 넘버 중복, `invalid_file`: 이미지 파일 형식 오류, `empty_fields`: 필수 필드 누락 |

### 4. 비고

X-Ray 이미지 업로드 시 클라이언트는 업로드된 이미지의 미리보기를 제공한다. 서버는 이미지 파일을 로컬 저장소에 저장하고 접근 가능한 `image_url`을 응답한다.

---

## 7. 진료기록 목록 조회 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 진료기록 목록 조회 API |
| 설명 | 로그인 사용자가 특정 환자의 진료기록 목록을 조회하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/{patient_id}/medical-records/` |
| 메서드(Method) | `GET` |
| 인증 필요 여부 | Y, `STAFF` 또는 `ADMIN` 권한 필요 |

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Authorization | `Bearer <access_token>` | JWT 액세스 토큰 |

#### 본문 예시

```json
{}
```

#### 본문 필드

| 파라미터명 | 타입 | 필수(Y/N) | 설명 |
| --- | --- | --- | --- |
| 없음 | - | - | - |

#### 쿼리 파라미터

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| page | integer | N | 페이지 번호. 기본값 `1` |
| size | integer | N | 페이지당 조회 수. 기본값 `20` |

### 3. 응답(Response)

#### 성공

`200 OK`

```json
{
  "total": 1,
  "page": 1,
  "size": 20,
  "items": [
    {
      "id": 1,
      "chart_number": "CHART-20260609-001",
      "symptoms": "기침과 흉통을 호소하며 흉부 X-Ray 촬영을 진행함",
      "created_at": "2026-06-09T10:10:00"
    }
  ]
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| total | integer | 해당 환자의 전체 진료기록 수 |
| page | integer | 현재 페이지 번호 |
| size | integer | 페이지당 조회 수 |
| items | array | 진료기록 목록 |

#### 실패

`404 Not Found`

```json
{
  "detail": "환자를 찾을 수 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `patient_not_found`: 대상 환자 없음 |

### 4. 비고

목록의 `symptoms`는 100자를 초과할 경우 클라이언트 또는 서버에서 말줄임표 형태로 축약해 표시할 수 있다.

---

## 8. 진료기록 상세 조회 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 진료기록 상세 조회 API |
| 설명 | 로그인 사용자가 특정 환자의 진료기록 상세정보와 흉부 X-Ray 이미지를 조회하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/{patient_id}/medical-records/{record_id}/` |
| 메서드(Method) | `GET` |
| 인증 필요 여부 | Y, `STAFF` 또는 `ADMIN` 권한 필요 |

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Authorization | `Bearer <access_token>` | JWT 액세스 토큰 |

#### 본문 예시

```json
{}
```

#### 본문 필드

| 파라미터명 | 타입 | 필수(Y/N) | 설명 |
| --- | --- | --- | --- |
| 없음 | - | - | - |

#### 쿼리 파라미터

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| 없음 | - | - | - |

### 3. 응답(Response)

#### 성공

`200 OK`

```json
{
  "id": 1,
  "patient_id": 1,
  "chart_number": "CHART-20260609-001",
  "symptoms": "기침과 흉통을 호소하며 흉부 X-Ray 촬영을 진행함",
  "xray_images": [
    {
      "id": 1,
      "image_url": "/media/xray/2026/06/chest-xray.png",
      "shooting_datetime": "2026-06-09T09:30:00",
      "created_at": "2026-06-09T10:10:00"
    }
  ],
  "created_at": "2026-06-09T10:10:00",
  "updated_at": null
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 진료기록 ID |
| patient_id | integer | 환자 고유 ID |
| chart_number | string | 차트 넘버 |
| symptoms | string | 증상 |
| xray_images | array | 흉부 X-Ray 이미지 목록 |
| created_at | datetime | 생성일시 |
| updated_at | datetime/null | 수정일시 |

#### 실패

`404 Not Found`

```json
{
  "detail": "진료기록을 찾을 수 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `patient_not_found`: 대상 환자 없음, `medical_record_not_found`: 대상 진료기록 없음 |

### 4. 비고

상세 조회 가능한 항목은 진료 기록 ID, 차트 넘버, 증상, 흉부 X-Ray 이미지, 생성일시이다. `record_id`는 요청한 `patient_id`에 속한 진료기록이어야 한다.

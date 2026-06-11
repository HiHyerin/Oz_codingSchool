# 폐렴예측 API 명세서

## 공통 사항

| 항목 | 내용 |
| --- | --- |
| Base URL | `/api/v1` |
| 인증 방식 | JWT Bearer Token |
| Access Token 만료 | 30분 |
| Refresh Token 만료 | 7일 |
| 공통 응답 시간 | 최대 3초 이내 |
| 예측 모델 파일 | `worker/models/model_state_dict.pth` |
| 예측 모델 로더 | `worker/model.py` |
| 모델 입력 이미지 | 진료기록 등록 시 업로드된 X-Ray 이미지 |

### 공통 Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | `application/json` | 요청 타입 |
| Authorization | `Bearer <access_token>` | 인증이 필요한 API 호출 시 사용 |

### 공통 Enum

| 구분 | 값 | 설명 |
| --- | --- | --- |
| role | `STAFF`, `ADMIN` | 폐렴 예측 API 접근 가능 권한 |
| prediction_label | `NORMAL`, `PNEUMONIA` | AI 모델 예측 라벨 |
| ai_model | `SimpleCNN-v1` | 폐렴 예측에 사용한 모델 식별자 |

### AI 예측 처리 규칙

| 항목 | 내용 |
| --- | --- |
| 입력 이미지 전처리 | 128x128 resize, grayscale 1 channel, tensor 변환 |
| 예측 함수 | `worker.model.predict_pneumonia(image_path)` |
| 폐렴 여부 판정 | `label == "PNEUMONIA"`이면 `is_pneumonia=true` |
| Confidence | 예측 라벨에 대한 확률값. `0.0` 이상 `1.0` 이하 |
| 중복 예측 처리 | 같은 진료기록과 같은 AI 모델의 예측 결과가 이미 있으면 재추론하지 않고 저장된 결과 반환 |
| Heatmap Image URL | 선택사항. 생성하지 않는 경우 `null` 또는 빈 문자열로 응답 |

---

## 1. AI 폐렴 예측 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | AI 폐렴 예측 API |
| 설명 | 진료기록에 저장된 X-Ray 이미지를 활용하여 폐렴 예측을 수행하고 결과를 저장 또는 조회하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/{patient_id}/medical-records/{record_id}/ai-analysis/` |
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
  "ai_model": "SimpleCNN-v1"
}
```

#### 본문 필드

| 파라미터명 | 타입 | 필수(Y/N) | 설명 |
| --- | --- | --- | --- |
| ai_model | string | N | 사용할 AI 모델 식별자. 기본값 `SimpleCNN-v1` |

#### 쿼리 파라미터

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| 없음 | - | - | - |

### 3. 응답(Response)

#### 성공

`200 OK`

이미 저장된 같은 모델의 예측 결과가 있거나, 새 예측을 수행한 뒤 저장에 성공한 경우 같은 형식으로 응답한다.

```json
{
  "id": 1,
  "record_id": 10,
  "is_pneumonia": true,
  "prediction_label": "PNEUMONIA",
  "confidence": 0.9234,
  "normal_probability": 0.0766,
  "pneumonia_probability": 0.9234,
  "heatmap_url": null,
  "ai_model": "SimpleCNN-v1",
  "is_cached": false,
  "created_at": "2026-06-11T10:00:00",
  "updated_at": null
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | AI 예측 결과 고유 ID |
| record_id | integer | 진료기록 ID |
| is_pneumonia | boolean | 폐렴 여부 |
| prediction_label | string | 모델 예측 라벨. `NORMAL` 또는 `PNEUMONIA` |
| confidence | number | 예측 라벨에 대한 confidence |
| normal_probability | number | 정상 판정 확률 |
| pneumonia_probability | number | 폐렴 판정 확률 |
| heatmap_url | string/null | Hitmap 또는 Heatmap 이미지 URL. 선택사항 |
| ai_model | string | 사용한 AI 모델 식별자 |
| is_cached | boolean | 기존 저장 결과 반환 여부 |
| created_at | datetime | 예측 수행 또는 저장 일시 |
| updated_at | datetime/null | 예측 결과 수정 일시 |

#### 실패

`404 Not Found`

```json
{
  "detail": "진료기록을 찾을 수 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `patient_not_found`: 대상 환자 없음, `medical_record_not_found`: 대상 진료기록 없음, `xray_image_not_found`: 예측에 사용할 X-Ray 이미지 없음 |

`500 Internal Server Error`

```json
{
  "detail": "AI 폐렴 예측 처리 중 오류가 발생했습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `model_load_error`: 모델 로드 실패, `prediction_failed`: 추론 실패, `save_failed`: 예측 결과 저장 실패 |

### 4. 비고

폐렴 예측 시 진료기록 등록 단계에서 업로드된 X-Ray 이미지를 사용한다. 같은 `record_id`와 `ai_model` 조합의 예측 결과가 이미 저장되어 있으면 모델 추론을 다시 수행하지 않고 저장된 데이터를 반환한다.

---

## 2. AI 폐렴 예측 결과 목록 조회 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | AI 폐렴 예측 결과 목록 조회 API |
| 설명 | 진료기록 상세 페이지의 AI 예측 결과 섹션에서 해당 진료기록의 폐렴 예측 결과 목록을 조회하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/{patient_id}/medical-records/{record_id}/ai-analysis/` |
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
      "record_id": 10,
      "is_pneumonia": true,
      "confidence": 0.9234,
      "heatmap_url": null,
      "ai_model": "SimpleCNN-v1",
      "created_at": "2026-06-11T10:00:00"
    }
  ]
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| total | integer | 해당 진료기록의 전체 AI 예측 결과 수 |
| page | integer | 현재 페이지 번호 |
| size | integer | 페이지당 조회 수 |
| items | array | AI 예측 결과 목록 |

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

목록에서 확인 가능한 항목은 고유 ID, 폐렴 여부, Confidence, Hitmap Image URL, 예측 수행 일시, 사용한 모델이다.

---

## 3. AI 폐렴 예측 결과 상세 조회 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | AI 폐렴 예측 결과 상세 조회 API |
| 설명 | 특정 AI 폐렴 예측 결과의 상세 확률과 메타데이터를 조회하는 API |
| 엔드포인트(Endpoint) | `/api/v1/patients/{patient_id}/medical-records/{record_id}/ai-analysis/{analysis_id}/` |
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
  "record_id": 10,
  "is_pneumonia": true,
  "prediction_label": "PNEUMONIA",
  "confidence": 0.9234,
  "normal_probability": 0.0766,
  "pneumonia_probability": 0.9234,
  "heatmap_url": null,
  "ai_model": "SimpleCNN-v1",
  "created_at": "2026-06-11T10:00:00",
  "updated_at": null
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | AI 예측 결과 고유 ID |
| record_id | integer | 진료기록 ID |
| is_pneumonia | boolean | 폐렴 여부 |
| prediction_label | string | 모델 예측 라벨 |
| confidence | number | 예측 라벨에 대한 confidence |
| normal_probability | number | 정상 판정 확률 |
| pneumonia_probability | number | 폐렴 판정 확률 |
| heatmap_url | string/null | Hitmap 또는 Heatmap 이미지 URL |
| ai_model | string | 사용한 AI 모델 식별자 |
| created_at | datetime | 예측 수행 또는 저장 일시 |
| updated_at | datetime/null | 예측 결과 수정 일시 |

#### 실패

`404 Not Found`

```json
{
  "detail": "AI 예측 결과를 찾을 수 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `patient_not_found`: 대상 환자 없음, `medical_record_not_found`: 대상 진료기록 없음, `analysis_result_not_found`: 대상 예측 결과 없음 |

### 4. 비고

상세 조회는 목록에서 선택한 AI 예측 결과의 전체 확률 정보와 사용 모델 정보를 확인할 때 사용한다. 기본 요구사항에는 목록 조회가 중심이지만, 프론트엔드 상세 표시와 디버깅을 위해 별도 상세 조회 API를 둔다.

---

## 비기능 요구사항

| 요구사항 ID | 항목 | 내용 |
| --- | --- | --- |
| NFR-PRED-001 | AI 모델 평가 기준 | Recall 최소 0.90 이상을 목표로 하며, 폐렴 환자를 정상으로 오진하는 FN을 가장 위험한 케이스로 관리한다. |
| NFR-PRED-001 | Accuracy | 보조 지표로 0.80 이상을 목표로 한다. |
| NFR-PRED-002 | API 성능 | 모든 폐렴 예측 API는 3초 이내 응답을 목표로 한다. |

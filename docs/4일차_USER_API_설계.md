# USER API 명세서

## 공통 사항

| 항목 | 내용 |
| --- | --- |
| Base URL | `/api/v1` |
| 인증 방식 | JWT Bearer Token |
| Access Token 만료 | 30분 |
| Refresh Token 만료 | 7일 |
| Refresh Token 전달 방식 | `HttpOnly` Cookie |
| JWT Payload | `user_id`만 저장 |
| 공통 응답 시간 | 최대 3초 이내 |

### 공통 Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | `application/json` | 요청 타입 |
| Authorization | `Bearer <access_token>` | 인증이 필요한 API 호출 시 사용 |

### 공통 Enum

| 구분 | 값 | 설명 |
| --- | --- | --- |
| gender | `M`, `F` | 성별 |
| department | `RESEARCH`, `MEDICAL`, `DEV` | 부서 |
| role | `PENDING`, `STAFF`, `ADMIN` | 권한 |

---

## 1. 회원가입 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 회원가입 API |
| 설명 | 이메일, 비밀번호, 이름, 부서, 성별, 휴대폰 번호를 입력하여 계정을 생성하는 API |
| 엔드포인트(Endpoint) | `/api/v1/auth/signup/` |
| 메서드(Method) | `POST` |
| 인증 필요 여부 | N |

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | `application/json` | 요청 타입 |

#### 본문 예시

```json
{
  "email": "doctor@example.com",
  "password": "securepassword",
  "name": "홍길동",
  "department": "MEDICAL",
  "gender": "M",
  "phone_number": "010-1234-5678"
}
```

#### 본문 필드

| 파라미터명 | 타입 | 필수(Y/N) | 설명 |
| --- | --- | --- | --- |
| email | string | Y | 사용자 이메일, 로그인 ID로 사용 |
| password | string | Y | 사용자 비밀번호 |
| name | string | Y | 사용자 이름 |
| department | string | Y | 부서. `RESEARCH`, `MEDICAL`, `DEV` 중 하나 |
| gender | string | Y | 성별. `M`, `F` 중 하나 |
| phone_number | string | Y | 휴대폰 번호 |

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
  "email": "doctor@example.com",
  "name": "홍길동",
  "department": "MEDICAL",
  "gender": "M",
  "phone_number": "010-1234-5678",
  "role": "PENDING",
  "is_active": true,
  "created_at": "2026-06-05T15:00:00",
  "updated_at": null
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 사용자 고유 ID |
| email | string | 사용자 이메일 |
| name | string | 사용자 이름 |
| department | string | 사용자 부서 |
| gender | string | 사용자 성별 |
| phone_number | string | 휴대폰 번호 |
| role | string | 사용자 권한. 기본값은 `PENDING` |
| is_active | boolean | 계정 활성화 여부 |
| created_at | datetime | 계정 생성 일시 |
| updated_at | datetime/null | 계정 수정 일시 |

#### 실패

`400 Bad Request`

```json
{
  "detail": "이미 사용 중인 이메일입니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `duplicate_email`: 이메일 중복, `duplicate_phone_number`: 휴대폰 번호 중복, `invalid_input`: 입력값 형식 오류, `empty_fields`: 필수 필드 누락 |

### 4. 비고

비밀번호는 평문이 아닌 암호화된 해시로 저장한다. 회원가입 직후 권한은 기본적으로 `PENDING`이며, 대기자는 마이페이지 외 서비스에 접근할 수 없다.

---

## 2. 로그인 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 사용자 로그인 API |
| 설명 | 이메일, 비밀번호를 활용한 로그인 API |
| 엔드포인트(Endpoint) | `/api/v1/auth/login/` |
| 메서드(Method) | `POST` |
| 인증 필요 여부 | N |

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | `application/json` | 요청 타입 |

#### 본문 예시

```json
{
  "email": "doctor@example.com",
  "password": "securepassword"
}
```

#### 본문 필드

| 파라미터명 | 타입 | 필수(Y/N) | 설명 |
| --- | --- | --- | --- |
| email | string | Y | 사용자 이메일 |
| password | string | Y | 사용자 비밀번호 |

#### 쿼리 파라미터

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| 없음 | - | - | - |

### 3. 응답(Response)

#### 성공

`200 OK`

```json
{
  "access_token": "string",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "doctor@example.com",
    "name": "홍길동",
    "role": "STAFF"
  }
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| access_token | string | JWT 액세스 토큰 |
| token_type | string | 토큰 타입. `bearer` |
| user | object | 로그인 사용자 정보 |

#### 실패

`400 Bad Request`

```json
{
  "detail": "이메일 또는 비밀번호가 일치하지 않습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `invalid_email_or_password`: 이메일 혹은 비밀번호 오류, `empty_fields`: 필수 필드 누락 |

### 4. 비고

Access Token은 응답 본문으로 전달하고 Refresh Token은 클라이언트 JavaScript에서 접근할 수 없도록 `HttpOnly` Cookie로 전달한다.

---

## 3. Access Token 재발급 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | Access Token 재발급 API |
| 설명 | Refresh Token을 검증하여 만료된 Access Token을 재발급하는 API |
| 엔드포인트(Endpoint) | `/api/v1/auth/refresh/` |
| 메서드(Method) | `POST` |
| 인증 필요 여부 | N |

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | `application/json` | 요청 타입 |
| Cookie | `refresh_token=<refresh_token>` | HttpOnly Cookie로 전달된 Refresh Token |

#### 본문 예시

```json
{}
```

#### 본문 필드

| 파라미터명 | 타입 | 필수(Y/N) | 설명 |
| --- | --- | --- | --- |
| 없음 | - | - | Refresh Token은 Cookie에서 읽음 |

#### 쿼리 파라미터

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| 없음 | - | - | - |

### 3. 응답(Response)

#### 성공

`200 OK`

```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| access_token | string | 새로 발급된 JWT 액세스 토큰 |
| token_type | string | 토큰 타입. `bearer` |

#### 실패

`401 Unauthorized`

```json
{
  "detail": "Refresh Token이 만료되었습니다. 다시 로그인해 주세요."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `missing_refresh_token`: Refresh Token 없음, `expired_refresh_token`: Refresh Token 만료, `invalid_refresh_token`: 유효하지 않은 Refresh Token |

### 4. 비고

Refresh Token도 만료된 경우 재로그인을 유도한다.

---

## 4. 로그아웃 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 로그아웃 API |
| 설명 | 로그인 사용자의 Refresh Token Cookie를 제거하고 로그아웃 처리하는 API |
| 엔드포인트(Endpoint) | `/api/v1/auth/logout/` |
| 메서드(Method) | `POST` |
| 인증 필요 여부 | Y |

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | `application/json` | 요청 타입 |
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
  "detail": "로그아웃되었습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | 로그아웃 처리 결과 메시지 |

#### 실패

`401 Unauthorized`

```json
{
  "detail": "인증 정보가 유효하지 않습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `invalid_token`: 토큰 오류, `expired_token`: Access Token 만료 |

### 4. 비고

로그아웃 성공 시 클라이언트는 로그인 페이지로 이동한다.

---

## 5. 회원 목록 조회 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 회원 목록 조회 API |
| 설명 | 관리자 권한 사용자가 전체 회원 목록을 조회하고 이메일, 이름, 부서로 검색/필터링하는 API |
| 엔드포인트(Endpoint) | `/api/v1/users/` |
| 메서드(Method) | `GET` |
| 인증 필요 여부 | Y, `ADMIN` 권한 필요 |

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
| search | string | N | 이메일 또는 이름 검색어 |
| department | string | N | 부서 필터. `RESEARCH`, `MEDICAL`, `DEV` 중 하나 |
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
      "email": "doctor@example.com",
      "name": "홍길동",
      "department": "MEDICAL",
      "gender": "M",
      "phone_number": "010-1234-5678",
      "role": "STAFF",
      "is_active": true
    }
  ]
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| total | integer | 전체 회원 수 |
| page | integer | 현재 페이지 |
| size | integer | 페이지당 조회 수 |
| items | array | 회원 목록 |

#### 실패

`403 Forbidden`

```json
{
  "detail": "관리자 권한이 필요합니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `admin_required`: 관리자 권한 없음 |

### 4. 비고

목록에서 확인 가능한 항목은 고유 ID, 이메일, 이름, 부서, 성별, 휴대폰 번호, 권한, 계정 활성화 여부이다.

---

## 6. 회원 권한 변경 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 회원 권한 변경 API |
| 설명 | 관리자 권한 사용자가 특정 회원의 권한을 변경하는 API |
| 엔드포인트(Endpoint) | `/api/v1/users/{user_id}/role/` |
| 메서드(Method) | `PATCH` |
| 인증 필요 여부 | Y, `ADMIN` 권한 필요 |

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | `application/json` | 요청 타입 |
| Authorization | `Bearer <access_token>` | JWT 액세스 토큰 |

#### 본문 예시

```json
{
  "role": "STAFF"
}
```

#### 본문 필드

| 파라미터명 | 타입 | 필수(Y/N) | 설명 |
| --- | --- | --- | --- |
| role | string | Y | 변경할 권한. `PENDING`, `STAFF`, `ADMIN` 중 하나 |

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
  "email": "doctor@example.com",
  "name": "홍길동",
  "role": "STAFF",
  "updated_at": "2026-06-05T15:30:00"
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 사용자 고유 ID |
| email | string | 사용자 이메일 |
| name | string | 사용자 이름 |
| role | string | 변경된 권한 |
| updated_at | datetime | 권한 변경 일시 |

#### 실패

`404 Not Found`

```json
{
  "detail": "회원을 찾을 수 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `user_not_found`: 대상 회원 없음, `invalid_role`: 변경할 권한 값 오류, `admin_required`: 관리자 권한 없음 |

### 4. 비고

`PENDING`은 마이페이지 외 모든 서비스 접근 불가, `STAFF`는 흉부 X-ray 관련 읽기/쓰기/수정 가능, `ADMIN`은 모든 항목에 대한 데이터 접근이 가능하다.

---

## 7. 마이페이지 조회 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 마이페이지 조회 API |
| 설명 | 로그인 사용자가 본인의 정보를 조회하는 API |
| 엔드포인트(Endpoint) | `/api/v1/users/me/` |
| 메서드(Method) | `GET` |
| 인증 필요 여부 | Y |

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
  "email": "doctor@example.com",
  "name": "홍길동",
  "department": "MEDICAL",
  "gender": "M",
  "phone_number": "010-1234-5678",
  "role": "STAFF",
  "is_active": true
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 사용자 고유 ID |
| email | string | 사용자 이메일 |
| name | string | 사용자 이름 |
| department | string | 사용자 부서 |
| gender | string | 사용자 성별 |
| phone_number | string | 휴대폰 번호 |
| role | string | 사용자 권한 |
| is_active | boolean | 계정 활성화 여부 |

#### 실패

`401 Unauthorized`

```json
{
  "detail": "인증 정보가 유효하지 않습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `invalid_token`: 토큰 오류, `expired_token`: Access Token 만료 |

### 4. 비고

모든 로그인 사용자가 접근 가능하며, `PENDING` 권한 사용자도 마이페이지는 조회할 수 있다.

---

## 8. 회원 정보 수정 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 회원 정보 수정 API |
| 설명 | 로그인 사용자가 본인의 부서와 휴대폰 번호를 부분 수정하는 API |
| 엔드포인트(Endpoint) | `/api/v1/users/me/` |
| 메서드(Method) | `PATCH` |
| 인증 필요 여부 | Y |

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | `application/json` | 요청 타입 |
| Authorization | `Bearer <access_token>` | JWT 액세스 토큰 |

#### 본문 예시

```json
{
  "department": "RESEARCH",
  "phone_number": "010-9876-5432"
}
```

#### 본문 필드

| 파라미터명 | 타입 | 필수(Y/N) | 설명 |
| --- | --- | --- | --- |
| department | string | N | 변경할 부서. `RESEARCH`, `MEDICAL`, `DEV` 중 하나 |
| phone_number | string | N | 변경할 휴대폰 번호 |

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
  "email": "doctor@example.com",
  "name": "홍길동",
  "department": "RESEARCH",
  "gender": "M",
  "phone_number": "010-9876-5432",
  "role": "STAFF",
  "is_active": true,
  "updated_at": "2026-06-05T16:00:00"
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| id | integer | 사용자 고유 ID |
| email | string | 사용자 이메일 |
| name | string | 사용자 이름 |
| department | string | 변경된 부서 |
| gender | string | 사용자 성별 |
| phone_number | string | 변경된 휴대폰 번호 |
| role | string | 사용자 권한 |
| is_active | boolean | 계정 활성화 여부 |
| updated_at | datetime | 정보 수정 일시 |

#### 실패

`400 Bad Request`

```json
{
  "detail": "수정 가능한 필드가 없습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `empty_update_fields`: 수정 필드 없음, `invalid_department`: 부서 값 오류, `duplicate_phone_number`: 휴대폰 번호 중복 |

### 4. 비고

회원 정보 수정은 Partial Update로 처리하며, 수정 가능한 항목은 부서와 휴대폰 번호로 제한한다.

---

## 9. 비밀번호 변경 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 비밀번호 변경 API |
| 설명 | 로그인 사용자가 기존 비밀번호 검증 후 새 비밀번호로 변경하는 API |
| 엔드포인트(Endpoint) | `/api/v1/users/me/password/` |
| 메서드(Method) | `PATCH` |
| 인증 필요 여부 | Y |

### 2. 요청(Request)

#### Headers

| Key | Value | 설명 |
| --- | --- | --- |
| Content-Type | `application/json` | 요청 타입 |
| Authorization | `Bearer <access_token>` | JWT 액세스 토큰 |

#### 본문 예시

```json
{
  "current_password": "oldpassword",
  "new_password": "newsecurepassword"
}
```

#### 본문 필드

| 파라미터명 | 타입 | 필수(Y/N) | 설명 |
| --- | --- | --- | --- |
| current_password | string | Y | 기존 비밀번호 |
| new_password | string | Y | 새 비밀번호 |

#### 쿼리 파라미터

| 쿼리 파라미터명 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| 없음 | - | - | - |

### 3. 응답(Response)

#### 성공

`200 OK`

```json
{
  "detail": "비밀번호가 변경되었습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | 비밀번호 변경 결과 메시지 |

#### 실패

`400 Bad Request`

```json
{
  "detail": "기존 비밀번호가 일치하지 않습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `invalid_current_password`: 기존 비밀번호 불일치, `same_as_current_password`: 기존 비밀번호와 새 비밀번호 동일, `empty_fields`: 필수 필드 누락 |

### 4. 비고

새 비밀번호는 평문이 아닌 암호화된 해시로 저장한다. 프론트엔드의 모든 비밀번호 입력란은 마스킹 처리하고, 보기 아이콘 클릭 시 입력값을 확인할 수 있도록 한다.

---

## 10. 회원 탈퇴 API

### 1. API 개요

| 항목 | 내용 |
| --- | --- |
| API 이름 | 회원 탈퇴 API |
| 설명 | 로그인 사용자가 본인 계정을 탈퇴하고 관련 정보를 즉시 삭제하는 API |
| 엔드포인트(Endpoint) | `/api/v1/users/me/` |
| 메서드(Method) | `DELETE` |
| 인증 필요 여부 | Y |

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

`401 Unauthorized`

```json
{
  "detail": "인증 정보가 유효하지 않습니다."
}
```

| 필드명 | 타입 | 설명 |
| --- | --- | --- |
| detail | string | `invalid_token`: 토큰 오류, `expired_token`: Access Token 만료 |

### 4. 비고

회원 탈퇴 시 Database에서 회원과 관련된 정보는 즉시 삭제한다. 탈퇴 성공 후 클라이언트는 로그인 페이지로 이동한다.
